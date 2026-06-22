from fastapi.testclient import TestClient

from app.main import app


def test_feedback_is_aggregated_without_id_labels() -> None:
    with TestClient(app) as client:
        generation = client.post(
            "/v1/generate",
            json={"prompt": "Give a concise observability definition."},
        )
        inference_id = generation.json()["inference_id"]
        response = client.post(
            "/v1/feedback",
            json={
                "inference_id": inference_id,
                "rating": 5,
                "helpful": True,
                "category": "accuracy",
            },
        )
        metrics = client.get("/metrics").text

    assert response.status_code == 202
    assert response.json() == {"status": "recorded"}
    assert 'llm_feedback_total{category="accuracy",sentiment="positive"}' in metrics
    assert 'llm_quality_rating_count{category="accuracy"}' in metrics
    assert inference_id not in metrics


def test_feedback_rating_is_validated() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/v1/feedback",
            json={
                "inference_id": "9d2c7e19-1361-47df-8b14-73157cdb50bd",
                "rating": 7,
                "helpful": False,
            },
        )

    assert response.status_code == 422
