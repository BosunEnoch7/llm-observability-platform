from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Iterator

if TYPE_CHECKING:
    from fastapi import FastAPI

from app.core.config import Settings, settings


def configure_tracing(application: "FastAPI", config: Settings) -> Any | None:
    if not config.otel_enabled:
        return None

    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased

    provider = TracerProvider(
        resource=Resource.create(
            {
                "service.name": config.otel_service_name,
                "deployment.environment": config.app_env,
            }
        ),
        sampler=ParentBased(TraceIdRatioBased(config.otel_trace_sample_ratio)),
    )
    exporter = OTLPSpanExporter(endpoint=config.otel_exporter_otlp_endpoint)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(application, tracer_provider=provider)
    return provider


@contextmanager
def provider_span(provider: str, model: str) -> Iterator[Any | None]:
    if not settings.otel_enabled:
        yield None
        return

    from opentelemetry import trace

    tracer = trace.get_tracer("llm-observability.provider")
    with tracer.start_as_current_span(
        "llm.provider.generate",
        attributes={
            "gen_ai.system": provider,
            "gen_ai.request.model": model,
        },
    ) as span:
        yield span


def current_trace_context() -> tuple[str | None, str | None]:
    if not settings.otel_enabled:
        return None, None
    try:
        from opentelemetry import trace
    except ImportError:
        return None, None

    context = trace.get_current_span().get_span_context()
    if not context.is_valid:
        return None, None
    return f"{context.trace_id:032x}", f"{context.span_id:016x}"
