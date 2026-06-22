from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    log_level: str = "INFO"
    llm_provider: Literal["simulated", "azure_openai"] = "simulated"
    default_model: str = "demo-model"
    llm_request_timeout_seconds: float = Field(default=30.0, gt=0, le=300)
    llm_max_retries: int = Field(default=2, ge=0, le=5)
    llm_retry_backoff_seconds: float = Field(default=0.25, ge=0, le=60)
    input_price_per_million_tokens: float = Field(default=1.0, ge=0)
    output_price_per_million_tokens: float = Field(default=2.0, ge=0)
    simulated_failure_rate: float = Field(default=0.0, ge=0, le=1)
    simulated_min_latency_ms: int = Field(default=100, ge=0)
    simulated_max_latency_ms: int = Field(default=500, ge=0)
    azure_openai_endpoint: str | None = None
    azure_openai_deployment: str | None = None
    azure_openai_api_version: str = "2024-10-21"
    azure_openai_api_key: SecretStr | None = None
    azure_use_managed_identity: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def validate_provider_configuration(self) -> "Settings":
        if self.simulated_min_latency_ms > self.simulated_max_latency_ms:
            raise ValueError(
                "SIMULATED_MIN_LATENCY_MS cannot exceed SIMULATED_MAX_LATENCY_MS"
            )
        if self.llm_provider != "azure_openai":
            return self
        if not self.azure_openai_endpoint or not self.azure_openai_deployment:
            raise ValueError(
                "Azure OpenAI requires AZURE_OPENAI_ENDPOINT and "
                "AZURE_OPENAI_DEPLOYMENT"
            )
        if not self.azure_use_managed_identity and (
            self.azure_openai_api_key is None
            or not self.azure_openai_api_key.get_secret_value()
        ):
            raise ValueError(
                "Set AZURE_OPENAI_API_KEY or enable AZURE_USE_MANAGED_IDENTITY"
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
