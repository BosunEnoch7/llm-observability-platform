from app.core.config import Settings
from app.providers.base import LLMProvider
from app.providers.simulated import SimulatedProvider


def build_provider(settings: Settings) -> LLMProvider:
    if settings.llm_provider == "azure_openai":
        from app.providers.azure_openai import AzureOpenAIProvider

        return AzureOpenAIProvider(settings)
    return SimulatedProvider(settings)
