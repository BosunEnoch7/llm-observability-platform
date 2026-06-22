from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_client import make_asgi_app

from app.api.health import router as health_router
from app.api.inference import router as inference_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.middleware.metrics import PrometheusMiddleware
from app.middleware.request_context import RequestContextMiddleware
from app.observability.metrics import SERVICE_INFO, SERVICE_READY
from app.observability.tracing import configure_tracing


@asynccontextmanager
async def lifespan(application: FastAPI):
    configure_logging()
    SERVICE_INFO.info({"environment": settings.app_env})
    SERVICE_READY.set(1)
    yield
    SERVICE_READY.set(0)
    tracer_provider = application.state.tracer_provider
    if tracer_provider is not None:
        tracer_provider.shutdown()


def create_app() -> FastAPI:
    application = FastAPI(
        title="LLM Observability Platform",
        version="0.2.0",
        lifespan=lifespan,
    )
    application.add_middleware(PrometheusMiddleware)
    application.add_middleware(RequestContextMiddleware)
    application.include_router(health_router)
    application.include_router(inference_router)
    application.mount("/metrics", make_asgi_app())
    application.state.tracer_provider = configure_tracing(application, settings)
    return application


app = create_app()
