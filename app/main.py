from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_client import make_asgi_app

from app.api.health import router as health_router
from app.api.inference import router as inference_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.middleware.metrics import PrometheusMiddleware
from app.observability.metrics import SERVICE_INFO, SERVICE_READY


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    SERVICE_INFO.info({"environment": settings.app_env})
    SERVICE_READY.set(1)
    yield
    SERVICE_READY.set(0)


def create_app() -> FastAPI:
    application = FastAPI(
        title="LLM Observability Platform",
        version="0.1.0",
        lifespan=lifespan,
    )
    application.add_middleware(PrometheusMiddleware)
    application.include_router(health_router)
    application.include_router(inference_router)
    application.mount("/metrics", make_asgi_app())
    return application


app = create_app()
