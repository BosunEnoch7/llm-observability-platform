from fastapi import APIRouter, Response, status

from app.observability.metrics import SERVICE_READY

router = APIRouter(tags=["health"])


@router.get("/health")
@router.get("/health/live")
async def liveness() -> dict[str, str]:
    return {"status": "healthy"}


@router.get("/health/ready")
async def readiness(response: Response) -> dict[str, str]:
    if SERVICE_READY._value.get() != 1:  # Prometheus Gauge has no public read API.
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "not_ready"}
    return {"status": "ready"}
