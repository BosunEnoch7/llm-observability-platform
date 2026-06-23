# Architecture overview

The FastAPI service owns LLM request instrumentation and exposes `/metrics` in
Prometheus format. Prometheus scrapes the service, evaluates alert rules, and
sends firing alerts to Alertmanager. Grafana queries Prometheus and provisions
the version-controlled LLM overview dashboard at startup.

The initial LLM implementation is deterministic infrastructure scaffolding with
configurable latency and failures. A real provider adapter can replace it
without changing the API or the metric contract.

The provider layer now supports both the simulator and Azure OpenAI. Reliability
controls live above the adapters so timeouts, retries, outcomes, logs, and
metrics behave consistently across providers. Each HTTP request receives a
correlation ID that is returned to the caller and included in structured logs.

Optional OpenTelemetry instrumentation creates inbound HTTP spans and nested
provider spans. OTLP export targets Jaeger locally and can be redirected to an
Azure-compatible telemetry pipeline during cloud promotion. Trace context is
added to JSON logs, but prompts and responses are excluded from span attributes.

AI-specific telemetry remains split by purpose. Prometheus stores aggregate,
bounded operational metrics for prompt versions, feedback, and safety events.
Inference IDs and any future detailed evaluation records belong in a durable,
access-controlled analytics system rather than metric labels or ordinary logs.

## Metric-label policy

Labels are restricted to bounded dimensions such as route, HTTP status, model,
direction, and outcome. Prompts, user identifiers, and request identifiers must
never be metric labels because they cause unbounded cardinality and may expose
sensitive data.
