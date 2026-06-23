# Distributed tracing

Tracing is disabled by default so the core service has no runtime dependency on
an available collector. Enable it in `.env`:

```dotenv
OTEL_ENABLED=true
OTEL_SERVICE_NAME=llm-observability-service
OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4317
OTEL_TRACE_SAMPLE_RATIO=1.0
```

After starting Compose, generate a request and open Jaeger at
<http://localhost:16686>. Select `llm-observability-service` to inspect the
FastAPI request and nested provider span.

Structured application logs include `request_id`, `trace_id`, and `span_id`,
which allows operators to move from an API response to logs and then a trace.
Only bounded operational attributes are recorded. Prompts, responses, API keys,
and user identifiers must not be attached to spans.

For Azure, the tracing bootstrap remains behind one application boundary. Cloud
promotion can replace the OTLP destination or add the Azure Monitor
OpenTelemetry distribution without changing request or provider code.

Production sampling should be chosen from traffic volume, retention, cost, and
incident requirements. The local default of 100% is intended for development,
not a blanket production recommendation.
