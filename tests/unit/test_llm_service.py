import asyncio

import pytest
from fastapi import HTTPException

from app.core.config import Settings
from app.providers.base import ProviderError, ProviderResult
from app.schemas.inference import GenerateRequest
from app.services.llm_service import LLMService


class SequenceProvider:
    name = "test"

    def __init__(self, outcomes: list[ProviderResult | Exception]):
        self.outcomes = outcomes
        self.calls = 0

    async def generate(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
    ) -> ProviderResult:
        outcome = self.outcomes[self.calls]
        self.calls += 1
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def test_provider_failure_is_retried() -> None:
    result = ProviderResult(
        model="test-model",
        text="ok",
        prompt_tokens=4,
        completion_tokens=2,
    )
    provider = SequenceProvider([ProviderError("temporary failure"), result])
    settings = Settings(llm_max_retries=1, llm_retry_backoff_seconds=0)
    service = LLMService(settings, provider)

    response = asyncio.run(service.generate(GenerateRequest(prompt="hello")))

    assert provider.calls == 2
    assert response.provider == "test"
    assert response.text == "ok"


def test_final_provider_failure_returns_503() -> None:
    provider = SequenceProvider([ProviderError("provider unavailable")])
    settings = Settings(llm_max_retries=0)
    service = LLMService(settings, provider)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(service.generate(GenerateRequest(prompt="hello")))

    assert exc_info.value.status_code == 503


def test_provider_timeout_returns_504() -> None:
    class SlowProvider:
        name = "slow"

        async def generate(self, prompt: str, model: str, max_tokens: int):
            await asyncio.sleep(0.05)
            raise AssertionError("request should have timed out")

    settings = Settings(llm_max_retries=0, llm_request_timeout_seconds=0.001)
    service = LLMService(settings, SlowProvider())

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(service.generate(GenerateRequest(prompt="hello")))

    assert exc_info.value.status_code == 504
