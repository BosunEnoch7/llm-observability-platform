# Architecture overview

The FastAPI service owns LLM request instrumentation and exposes `/metrics` in
Prometheus format. Prometheus scrapes the service, evaluates alert rules, and
sends firing alerts to Alertmanager. Grafana queries Prometheus and provisions
the version-controlled LLM overview dashboard at startup.

The initial LLM implementation is deterministic infrastructure scaffolding with
configurable latency and failures. A real provider adapter can replace it
without changing the API or the metric contract.

## Metric-label policy

Labels are restricted to bounded dimensions such as route, HTTP status, model,
direction, and outcome. Prompts, user identifiers, and request identifiers must
never be metric labels because they cause unbounded cardinality and may expose
sensitive data.
