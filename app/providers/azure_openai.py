from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AsyncAzureOpenAI, OpenAIError

from app.core.config import Settings
from app.providers.base import ProviderError, ProviderResult

AZURE_COGNITIVE_SERVICES_SCOPE = "https://cognitiveservices.azure.com/.default"


class AzureOpenAIProvider:
    name = "azure_openai"

    def __init__(self, settings: Settings):
        client_options: dict[str, object] = {
            "azure_endpoint": settings.azure_openai_endpoint,
            "api_version": settings.azure_openai_api_version,
            "max_retries": 0,
        }
        if settings.azure_use_managed_identity:
            credential = DefaultAzureCredential()
            client_options["azure_ad_token_provider"] = get_bearer_token_provider(
                credential,
                AZURE_COGNITIVE_SERVICES_SCOPE,
            )
        else:
            assert settings.azure_openai_api_key is not None
            client_options["api_key"] = settings.azure_openai_api_key.get_secret_value()

        self.deployment = settings.azure_openai_deployment or ""
        self.client = AsyncAzureOpenAI(**client_options)

    async def generate(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
    ) -> ProviderResult:
        try:
            response = await self.client.chat.completions.create(
                model=self.deployment,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
            )
        except OpenAIError as exc:
            raise ProviderError("Azure OpenAI request failed") from exc

        usage = response.usage
        choice = response.choices[0] if response.choices else None
        if usage is None or choice is None or choice.message.content is None:
            raise ProviderError("Azure OpenAI returned an incomplete response")

        return ProviderResult(
            model=model,
            text=choice.message.content,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
        )
