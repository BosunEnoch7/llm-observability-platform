import asyncio
import logging
import time

from fastapi import HTTPException

from app.core.config import Settings
from app.observability.metrics import (
    ESTIMATED_COST,
    INFERENCE_DURATION,
    INFERENCE_REQUESTS,
    PROVIDER_ATTEMPTS,
    PROVIDER_RETRIES,
    TOKENS,
)
from app.providers import LLMProvider, ProviderError, build_provider
from app.schemas.inference import GenerateRequest, GenerateResponse, Usage

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self, settings: Settings, provider: LLMProvider | None = None):
        self.settings = settings
        self.provider = provider or build_provider(settings)

    async def generate(self, request: GenerateRequest) -> GenerateResponse:
        model = request.model or self.settings.default_model
        started = time.perf_counter()
        outcome = "error"
        try:
            result = await self._generate_with_retry(request, model)
            cost = (
                result.prompt_tokens * self.settings.input_price_per_million_tokens
                + result.completion_tokens
                * self.settings.output_price_per_million_tokens
            ) / 1_000_000

            TOKENS.labels(model=model, direction="input").inc(result.prompt_tokens)
            TOKENS.labels(model=model, direction="output").inc(result.completion_tokens)
            ESTIMATED_COST.labels(model=model).inc(cost)
            outcome = "success"

            usage = Usage(
                prompt_tokens=result.prompt_tokens,
                completion_tokens=result.completion_tokens,
                total_tokens=result.prompt_tokens + result.completion_tokens,
            )
            return GenerateResponse(
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

    async def _generate_with_retry(
        self,
        request: GenerateRequest,
        model: str,
    ):
        attempts = self.settings.llm_max_retries + 1
        for attempt in range(attempts):
            try:
                result = await asyncio.wait_for(
                    self.provider.generate(request.prompt, model, request.max_tokens),
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
