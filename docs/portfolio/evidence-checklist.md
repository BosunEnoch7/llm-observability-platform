# Portfolio evidence checklist

Use this checklist when preparing the final project screenshots and README
evidence.

## Required screenshots

- [x] `screenshots/01-api-docs.png` - FastAPI Swagger UI at `/docs`.
- [x] `screenshots/02-health-ready.png` - `/health/ready` returning ready status.
- [x] `screenshots/03-metrics.png` - `/metrics` showing LLM metrics.
- [x] `screenshots/04-prometheus-targets.png` - Prometheus target for the LLM
  service in the `UP` state.
- [x] `screenshots/05-prometheus-rules.png` - loaded alert and SLO rules.
- [x] `screenshots/06-grafana-overview.png` - live LLM overview dashboard.
- [x] `screenshots/07-alertmanager.png` - Alertmanager ready status.
- [x] `screenshots/08-jaeger-trace.png` - LLM service traces.
- [x] `screenshots/09-load-test.png` - controlled load-test output.
- [x] `screenshots/10-github-actions-ci.png` - successful CI workflow.
- [x] `screenshots/11-azure-deploy-workflow.png` - Azure deploy workflow.
- [ ] `screenshots/12-azure-resources.png` - intentionally absent until an
  authorized deployment succeeds. The current subscription quota blocker is
  documented rather than disguised.

## Machine-readable evidence

- `screenshots/evidence/summary.json` - local evidence collection summary.
- `screenshots/evidence/health-ready.json` - readiness proof.
- `screenshots/evidence/metrics.txt` - API metrics proof.
- `screenshots/evidence/prometheus-targets.json` - scrape target proof.
- `screenshots/evidence/prometheus-rules.json` - alert rule proof.
- `screenshots/evidence/load-test.txt` - first controlled load-test output.
- `screenshots/evidence/load-test-live.txt` - load used for live dashboard proof.

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
