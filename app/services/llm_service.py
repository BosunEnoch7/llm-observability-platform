import asyncio
import random
import time

from fastapi import HTTPException

from app.core.config import Settings
from app.observability.metrics import (
    ESTIMATED_COST,
    INFERENCE_DURATION,
    INFERENCE_REQUESTS,
    TOKENS,
)
from app.schemas.inference import GenerateRequest, GenerateResponse, Usage

# Demonstration prices per one million tokens. Replace with provider configuration later.
INPUT_PRICE_PER_MILLION = 1.00
OUTPUT_PRICE_PER_MILLION = 2.00


class LLMService:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def generate(self, request: GenerateRequest) -> GenerateResponse:
        model = request.model or self.settings.default_model
        started = time.perf_counter()
        try:
            delay_ms = random.randint(
                self.settings.simulated_min_latency_ms,
                self.settings.simulated_max_latency_ms,
            )
            await asyncio.sleep(delay_ms / 1000)
            if random.random() < self.settings.simulated_failure_rate:
                raise RuntimeError("simulated provider failure")

            prompt_tokens = max(1, len(request.prompt) // 4)
            completion_tokens = min(request.max_tokens, max(8, prompt_tokens // 2))
            cost = (
                prompt_tokens * INPUT_PRICE_PER_MILLION
                + completion_tokens * OUTPUT_PRICE_PER_MILLION
            ) / 1_000_000

            TOKENS.labels(model=model, direction="input").inc(prompt_tokens)
            TOKENS.labels(model=model, direction="output").inc(completion_tokens)
            ESTIMATED_COST.labels(model=model).inc(cost)
            INFERENCE_REQUESTS.labels(model=model, outcome="success").inc()

            usage = Usage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            )
            return GenerateResponse(
                model=model,
                text=f"Simulated response for: {request.prompt[:120]}",
                usage=usage,
                estimated_cost_usd=round(cost, 8),
            )
        except RuntimeError as exc:
            INFERENCE_REQUESTS.labels(model=model, outcome="error").inc()
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        finally:
            INFERENCE_DURATION.labels(model=model).observe(time.perf_counter() - started)
