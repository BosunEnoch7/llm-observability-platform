from fastapi.testclient import TestClient

from app.main import app


def test_generation_is_reflected_in_metrics() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/v1/generate",
            json={"prompt": "Explain why observability matters.", "max_tokens": 32},
        )
        metrics = client.get("/metrics").text

    assert response.status_code == 200
    assert response.json()["usage"]["total_tokens"] > 0
    assert "llm_inference_requests_total" in metrics
    assert "llm_tokens_total" in metrics
    assert "llm_estimated_cost_usd_total" in metrics
