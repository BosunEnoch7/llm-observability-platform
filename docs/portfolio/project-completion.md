# Project completion report

## Completion status

The project is implementation-complete for the local and repository-delivered
scope. The remaining external gate is an authorized Azure subscription
deployment, which requires GitHub environment variables, Azure permissions,
quota, and approved cost ownership.

For a concise operator handoff, see [final handoff](final-handoff.md).

## Delivered capabilities

- FastAPI LLM workload service with health, readiness, generation, feedback, and
  Prometheus metrics endpoints.
- Simulated LLM provider for deterministic local testing.
- Azure OpenAI provider adapter with managed identity support.
- Request, error, latency, token, estimated cost, retry, provider, prompt
  version, safety, and quality metrics.
- Prometheus scrape configuration and alert rules.
- Grafana datasource and LLM overview dashboard provisioning.
- Alertmanager routing placeholder for production notification integration.
- Optional OpenTelemetry tracing to Jaeger with trace/log correlation.
- SLO documentation and multi-window availability burn-rate alerts.
- Local load testing and controlled failure injection workflow.
- Docker Compose local operations stack.
- GitHub Actions CI with tests, linting, Docker build, and Bicep compilation.
- Azure Bicep infrastructure for ACR, Container Apps, managed identity, Key
  Vault, Log Analytics, optional Azure OpenAI, optional Azure Monitor workspace,
  and optional Azure Managed Grafana.
- GitHub Actions deployment workflow using Azure OIDC.
- Runbooks, Azure deployment docs, and project incident/blocker history.

## Production-style SRE practices demonstrated

- Health and readiness separation.
- Bounded-cardinality metric labels.
- Alert rules mapped to operator runbooks.
- Error-budget thinking with SLO burn-rate alerts.
- Immutable container image deployment by commit SHA.
- Managed identity preference over static credentials.
- Infrastructure-as-code validation in CI.
- Incident/blocker logging with treatment and follow-up.
- Local failure injection before cloud rollout.
- Clear distinction between local demo controls and production safety/governance
  requirements.

## External deployment gate

The Azure deployment workflow is ready, but should only be executed after:

1. GitHub environments `dev`, `staging`, and `prod` are created.
2. `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, and `AZURE_SUBSCRIPTION_ID` are set as
   GitHub environment variables.
3. The federated identity has the required Azure RBAC permissions.
4. Azure resource providers are registered.
5. Regional Azure OpenAI availability, quota, and cost ownership are confirmed.
6. A Bicep `what-if` review is completed.

Until those items are complete, the responsible status is:

> Local/repository implementation complete; real Azure deployment pending
> authorized cloud access and cost approval.

## Final validation command set

```powershell
$env:AZURE_CONFIG_DIR="$PWD\.azure-local"
az bicep build --file infra/bicep/foundation.bicep --stdout | Out-Null
az bicep build --file infra/bicep/app.bicep --stdout | Out-Null
az bicep build-params --file infra/bicep/foundation.dev.bicepparam --stdout | Out-Null
.\.venv\Scripts\python.exe -m pytest --cov=app --cov-report=term-missing
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
docker compose config | Out-Null
.\.venv\Scripts\python.exe -m json.tool grafana/dashboards/llm-overview.json | Out-Null
```
