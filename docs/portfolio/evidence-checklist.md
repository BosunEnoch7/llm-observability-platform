# Portfolio evidence checklist

Use this checklist when preparing the final project screenshots and README
evidence.

## Required screenshots

- `screenshots/01-api-docs.png` — FastAPI Swagger UI at `/docs`.
- `screenshots/02-health-ready.png` — `/health/ready` returning ready status.
- `screenshots/03-metrics.png` — `/metrics` showing LLM metrics.
- `screenshots/04-prometheus-targets.png` — Prometheus target for the LLM
  service in the `UP` state.
- `screenshots/05-prometheus-rules.png` — loaded alert rules.
- `screenshots/06-grafana-overview.png` — LLM overview dashboard.
- `screenshots/07-alertmanager.png` — Alertmanager route/status page.
- `screenshots/08-jaeger-trace.png` — request trace with provider span.
- `screenshots/09-load-test.png` — load/failure test output.
- `screenshots/10-github-actions-ci.png` — successful CI workflow.
- `screenshots/11-azure-deploy-workflow.png` — Azure deploy workflow inputs.
- `screenshots/12-azure-resources.png` — Azure resources after authorized
  deployment, when available.

## Evidence narrative

When presenting the project, explain:

1. what problem LLM observability solves;
2. what signals are collected and why;
3. how metrics avoid sensitive prompts and high-cardinality labels;
4. how SLOs and alerts map to runbooks;
5. how failures are injected and investigated;
6. how Azure deployment uses managed identity and GitHub OIDC;
7. what incidents/blockers occurred during the build and how they were treated.

## Final review checklist

- README quick start works.
- Tests and lint pass.
- Docker Compose starts the local stack.
- Prometheus can scrape the app.
- Grafana dashboard loads automatically.
- Alert rules are visible in Prometheus.
- Incident log is updated.
- Screenshots are placed in `screenshots/`.
- Real Azure deployment status is clearly stated.
