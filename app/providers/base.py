from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ProviderResult:
    model: str
    text: str
    prompt_tokens: int
    completion_tokens: int


class ProviderError(RuntimeError):
    """A sanitized provider failure safe to expose through the API."""


class LLMProvider(Protocol):
    name: str

    async def generate(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
    ) -> ProviderResult: ...
