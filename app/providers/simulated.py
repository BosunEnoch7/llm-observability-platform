import asyncio
import random

from app.core.config import Settings
from app.providers.base import ProviderError, ProviderResult


class SimulatedProvider:
    name = "simulated"

    def __init__(self, settings: Settings):
        self.settings = settings

    async def generate(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
    ) -> ProviderResult:
        delay_ms = random.randint(
            self.settings.simulated_min_latency_ms,
            self.settings.simulated_max_latency_ms,
        )
        await asyncio.sleep(delay_ms / 1000)
        if random.random() < self.settings.simulated_failure_rate:
            raise ProviderError("simulated provider failure")

        prompt_tokens = max(1, len(prompt) // 4)
        completion_tokens = min(max_tokens, max(8, prompt_tokens // 2))
        return ProviderResult(
            model=model,
            text=f"Simulated response for: {prompt[:120]}",
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )
