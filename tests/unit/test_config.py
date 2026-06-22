import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_azure_provider_requires_endpoint_and_deployment() -> None:
    with pytest.raises(ValidationError):
        Settings(llm_provider="azure_openai")


def test_azure_api_key_mode_requires_key() -> None:
    with pytest.raises(ValidationError):
        Settings(
            llm_provider="azure_openai",
            azure_openai_endpoint="https://example.openai.azure.com",
            azure_openai_deployment="example",
            azure_use_managed_identity=False,
        )


def test_simulated_latency_range_is_validated() -> None:
    with pytest.raises(ValidationError):
        Settings(simulated_min_latency_ms=100, simulated_max_latency_ms=10)
