import sys
from contextlib import contextmanager
from types import ModuleType

from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.observability.tracing import current_trace_context, provider_span


class FakeSpanContext:
    is_valid = True
    trace_id = 0x123
    span_id = 0x456


class FakeSpan:
    def get_span_context(self) -> FakeSpanContext:
        return FakeSpanContext()


class FakeTracer:
    @contextmanager
    def start_as_current_span(self, name: str, attributes: dict[str, str]):
        assert name == "llm.provider.generate"
        assert attributes["gen_ai.system"] == "simulated"
        yield FakeSpan()


def install_fake_opentelemetry(monkeypatch) -> None:
    trace = ModuleType("opentelemetry.trace")
    trace.get_current_span = lambda: FakeSpan()
    trace.get_tracer = lambda _: FakeTracer()
    package = ModuleType("opentelemetry")
    package.trace = trace
    monkeypatch.setitem(sys.modules, "opentelemetry", package)
    monkeypatch.setitem(sys.modules, "opentelemetry.trace", trace)


def test_active_trace_context_is_formatted(monkeypatch) -> None:
    install_fake_opentelemetry(monkeypatch)
    monkeypatch.setattr(settings, "otel_enabled", True)

    trace_id, span_id = current_trace_context()

    assert trace_id == f"{0x123:032x}"
    assert span_id == f"{0x456:016x}"


def test_provider_span_uses_bounded_attributes(monkeypatch) -> None:
    install_fake_opentelemetry(monkeypatch)
    monkeypatch.setattr(settings, "otel_enabled", True)

    with provider_span("simulated", "demo-model") as span:
        assert isinstance(span, FakeSpan)


def test_tracer_provider_is_shutdown() -> None:
    class FakeProvider:
        stopped = False

        def shutdown(self) -> None:
            self.stopped = True

    provider = FakeProvider()
    original = app.state.tracer_provider
    app.state.tracer_provider = provider
    try:
        with TestClient(app):
            pass
    finally:
        app.state.tracer_provider = original

    assert provider.stopped is True
