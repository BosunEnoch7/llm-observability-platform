import asyncio
import logging
import time
from uuid import uuid4

from fastapi import HTTPException

from app.core.config import Settings
from app.observability.metrics import (
    ESTIMATED_COST,
    INFERENCE_DURATION,
    INFERENCE_REQUESTS,
    PROVIDER_ATTEMPTS,
    PROVIDER_RETRIES,
    PROMPT_VERSION_REQUESTS,
    SAFETY_EVALUATIONS,
    SAFETY_EVENTS,
    TOKENS,
)
from app.observability.tracing import provider_span
from app.providers import LLMProvider, ProviderError, build_provider
from app.schemas.inference import GenerateRequest, GenerateResponse, Usage
from app.services.safety_service import SafetyEvaluator

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(
        self,
        settings: Settings,
        provider: LLMProvider | None = None,
        safety_evaluator: SafetyEvaluator | None = None,
    ):
        self.settings = settings
        self.provider = provider or build_provider(settings)
        self.safety_evaluator = safety_evaluator or SafetyEvaluator()

    async def generate(self, request: GenerateRequest) -> GenerateResponse:
        model = request.model or self.settings.default_model
        started = time.perf_counter()
        outcome = "error"
        PROMPT_VERSION_REQUESTS.labels(
            model=model,
            prompt_version=self.settings.prompt_version,
        ).inc()
        try:
            if self._evaluate_safety(request.prompt, "input"):
                outcome = "blocked"
                raise HTTPException(
                    status_code=422, detail="Input blocked by safety policy"
                )

            result = await self._generate_with_retry(request, model)
            cost = (
                result.prompt_tokens * self.settings.input_price_per_million_tokens
                + result.completion_tokens
                * self.settings.output_price_per_million_tokens
            ) / 1_000_000

            TOKENS.labels(model=model, direction="input").inc(result.prompt_tokens)
            TOKENS.labels(model=model, direction="output").inc(result.completion_tokens)
            ESTIMATED_COST.labels(model=model).inc(cost)

            if self._evaluate_safety(result.text, "output"):
                outcome = "blocked"
                raise HTTPException(
                    status_code=422,
                    detail="Output blocked by safety policy",
                )
            outcome = "success"

            usage = Usage(
                prompt_tokens=result.prompt_tokens,
                completion_tokens=result.completion_tokens,
                total_tokens=result.prompt_tokens + result.completion_tokens,
            )
            return GenerateResponse(
                inference_id=uuid4(),
                prompt_version=self.settings.prompt_version,
                provider=self.provider.name,
                model=result.model,
                text=result.text,
                usage=usage,
                estimated_cost_usd=round(cost, 8),
            )
        finally:
            INFERENCE_REQUESTS.labels(model=model, outcome=outcome).inc()
            INFERENCE_DURATION.labels(model=model).observe(
                time.perf_counter() - started
            )

    def _evaluate_safety(self, text: str, stage: str) -> bool:
        if self.settings.safety_mode == "disabled":
            return False

        findings = self.safety_evaluator.evaluate(text)
        SAFETY_EVALUATIONS.labels(
            stage=stage,
            outcome="flagged" if findings else "clear",
        ).inc()
        blocked = bool(findings) and self.settings.safety_mode == "enforce"
        for finding in findings:
            SAFETY_EVENTS.labels(
                stage=stage,
                category=finding.category,
                action="blocked" if blocked else "observed",
            ).inc()
        return blocked

    async def _generate_with_retry(
        self,
        request: GenerateRequest,
        model: str,
    ):
        attempts = self.settings.llm_max_retries + 1
        for attempt in range(attempts):
            try:
                with provider_span(self.provider.name, model):
                    result = await asyncio.wait_for(
                        self.provider.generate(
                            request.prompt, model, request.max_tokens
                        ),
                        timeout=self.settings.llm_request_timeout_seconds,
                    )
                PROVIDER_ATTEMPTS.labels(
                    provider=self.provider.name,
                    outcome="success",
                ).inc()
                return result
            except TimeoutError as exc:
                PROVIDER_ATTEMPTS.labels(
                    provider=self.provider.name,
                    outcome="timeout",
                ).inc()
                if attempt == attempts - 1:
                    logger.warning("LLM provider request timed out")
                    raise HTTPException(
                        status_code=504,
                        detail="LLM provider request timed out",
                    ) from exc
            except ProviderError as exc:
                PROVIDER_ATTEMPTS.labels(
                    provider=self.provider.name,
                    outcome="error",
                ).inc()
                if attempt == attempts - 1:
                    logger.warning("LLM provider request failed")
                    raise HTTPException(status_code=503, detail=str(exc)) from exc

            PROVIDER_RETRIES.labels(provider=self.provider.name).inc()
            logger.info("Retrying LLM provider request", extra={"attempt": attempt + 2})
            await asyncio.sleep(self.settings.llm_retry_backoff_seconds * (2**attempt))

        raise RuntimeError("unreachable")
