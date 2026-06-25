# LLM Observability Platform

[![CI](https://github.com/BosunEnoch7/llm-observability-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/BosunEnoch7/llm-observability-platform/actions/workflows/ci.yml)

Production-style observability platform for Large Language Model workloads,
built to demonstrate AI DevOps, SRE, monitoring, alerting, cloud readiness, and
operational documentation.

This project shows how an LLM service can be instrumented, monitored, tested,
alerted on, documented, and prepared for Azure deployment using modern DevOps
practices.

## Executive summary

The platform provides a FastAPI-based LLM workload service with Prometheus
metrics, Grafana dashboards, Alertmanager readiness, SLOs, runbooks, failure
testing, quality/safety telemetry, GitHub Actions CI, and Azure-ready
infrastructure-as-code.

It is intentionally designed like a production platform:

- observable by default;
- safe for local demos without real API keys;
- ready for Azure promotion through Bicep and GitHub OIDC;
- documented with runbooks, SLOs, incident history, and handoff notes.

## Current status

Repository implementation is complete.

The complete local Docker Compose stack has been started and verified. Runtime
evidence includes API health, generation, feedback, metrics, Prometheus scrape
targets, and loaded alert rules. Grafana health is confirmed; optional visual
screenshots can be captured from the running local dashboard.

Real Azure deployment requires authorized subscription access, GitHub OIDC
variables, RBAC, quota, and cost approval.

This status is documented honestly because production engineering should not
claim cloud deployment or dashboard proof that has not been executed.

## What this project demonstrates

- AI observability for LLM workloads
- Request, latency, error, token, and cost telemetry
- Prometheus metrics and PromQL alert rules
- Grafana dashboard provisioning
- Alertmanager routing readiness
- Health and readiness probes
- SLOs and multi-window burn-rate alerting
- Load testing and controlled failure injection
- Structured JSON logs and correlation IDs
- Optional OpenTelemetry tracing with Jaeger
- Azure OpenAI provider adapter with managed identity support
- Secure configuration practices
- GitHub Actions CI and deployment workflow
- Azure Bicep infrastructure
- GitHub OIDC cloud deployment readiness
- Incident/blocker documentation and operational handoff

## Technology stack

| Area | Tools |
| --- | --- |
| API service | Python, FastAPI, Pydantic |
| Metrics | prometheus-client, Prometheus |
| Dashboards | Grafana |
| Alerts | Prometheus alert rules, Alertmanager |
| Tracing | OpenTelemetry, Jaeger |
| Runtime | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Cloud target | Azure Container Apps, ACR, Key Vault, Managed Identity, Azure OpenAI |
| Infrastructure | Azure Bicep |
| Testing | Pytest, Ruff, custom load testing |

## Architecture

```text
Client
  |
  v
FastAPI LLM Service ---> LLM Provider
  |
  +-- /health/live
  +-- /health/ready
  +-- /metrics --------> Prometheus ------> Grafana
  |                         |
  |                         +-----------> Alertmanager
  |
  +-- OTLP traces ------> Jaeger
```

For cloud promotion, the target path is:

```text
GitHub Actions
  |
  +-- GitHub OIDC
  |
  v
Azure
  |
  +-- Azure Container Registry
  +-- Azure Container Apps
  +-- Managed Identity
  +-- Key Vault
  +-- Azure OpenAI
  +-- Azure Monitor / Managed Grafana
```

## Key observability signals

| Signal | Metric | Why it matters |
| --- | --- | --- |
| Request count | `llm_http_requests_total` | Measures traffic volume and HTTP outcomes |
| HTTP latency | `llm_http_request_duration_seconds` | Tracks user-facing API performance |
| Inference latency | `llm_inference_duration_seconds` | Tracks model/provider performance |
| Inference outcomes | `llm_inference_requests_total` | Separates successful and failed generations |
| Provider attempts | `llm_provider_attempts_total` | Shows provider success, error, and timeout attempts |
| Provider retries | `llm_provider_retries_total` | Highlights dependency instability |
| Token usage | `llm_tokens_total` | Tracks input/output consumption |
| Estimated cost | `llm_estimated_cost_usd_total` | Provides cost visibility |
| Prompt versions | `llm_prompt_version_requests_total` | Tracks prompt release adoption |
| Safety events | `llm_safety_events_total` | Captures bounded safety categories/actions |
| Quality ratings | `llm_quality_rating` | Tracks aggregate feedback quality |
| Readiness | `llm_service_ready` | Indicates whether service should receive traffic |
| Scrape health | Prometheus `up` | Confirms target reachability |

Metric labels intentionally avoid prompts, user IDs, request IDs, and other
unbounded or sensitive values.

## Production-style practices included

- Bounded-cardinality metrics
- Separate liveness and readiness endpoints
- Timeouts and observable retries
- SLO and error-budget thinking
- Runbooks linked to alerts
- Failure injection for reliability testing
- Safe local simulator for repeatable demos
- Managed identity preferred over static secrets
- Azure deployment preflight before cloud changes
- Teardown and cost-control documentation
- Incident/blocker log with treatment and follow-up

## Quick start with Docker Compose

Requirements:

- Docker Desktop or Docker Engine
- Docker Compose

```bash
cp .env.example .env
docker compose up --build -d
docker compose ps
```

PowerShell:

```powershell
Copy-Item .env.example .env
docker compose up --build -d
docker compose ps
```

Open the services:

| Service | URL | Local credentials |
| --- | --- | --- |
| FastAPI docs | <http://localhost:8000/docs> | None |
| Metrics endpoint | <http://localhost:8000/metrics> | None |
| Prometheus | <http://localhost:9090> | None |
| Grafana | <http://localhost:3000> | `admin` / `admin` |
| Alertmanager | <http://localhost:9093> | None |
| Jaeger | <http://localhost:16686> | None |

Run a smoke test:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke-test.ps1
```

Collect local evidence:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\collect-local-evidence.ps1
```

If Docker is unavailable, run the API directly and collect API-only evidence:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
powershell -ExecutionPolicy Bypass -File .\scripts\collect-local-evidence.ps1 -SkipPrometheus
```

## Local development

```bash
python -m venv .venv
python -m pip install -r requirements-dev.txt
python -m pytest
python -m ruff check .
uvicorn app.main:app --reload
```

Makefile shortcuts:

```bash
make validate
make up
make smoke
make evidence
make load
make failure-up
make azure-preflight
make azure-teardown-dry-run
```

## Testing and validation

Latest validation snapshot:

- 19 tests passed
- 87% coverage
- Ruff lint passed
- Ruff format check passed
- Bicep templates compile
- Grafana dashboard JSON validates
- Docker Compose stack verified across five services
- Grafana database health reports `ok`
- Prometheus reports two active targets and four rule groups
- Full local machine-readable evidence collected successfully

The CI workflow validates tests, linting, Docker build readiness, and Bicep
compilation.

## Azure readiness

The project includes Azure Bicep templates and a GitHub Actions deployment
workflow.

Provisioned foundation:

- Azure Resource Group
- Azure Container Registry
- Azure Container Apps environment
- User-assigned Managed Identity
- RBAC-enabled Key Vault
- Log Analytics
- Optional Azure OpenAI
- Optional Azure Monitor workspace
- Optional Azure Managed Grafana

Azure deployment path:

```powershell
$env:AZURE_CONFIG_DIR="$PWD\.azure-local"
az login
az account set --subscription "<subscription-id>"
.\scripts\azure-preflight.ps1 -EnvironmentName dev -Location eastus2
.\scripts\azure-oidc-bootstrap.ps1 `
  -GitHubOrg "BosunEnoch7" `
  -GitHubRepo "llm-observability-platform" `
  -SubscriptionId "<subscription-id>"
```

Then run Bicep what-if:

```powershell
az deployment sub what-if `
  --location eastus2 `
  --template-file infra/bicep/foundation.bicep `
  --parameters location=eastus2 environmentName=dev
```

After approval, trigger the GitHub Actions **Deploy to Azure** workflow for
`dev`.

Current Azure execution status: authentication and preflight passed, but the
selected subscription's single Container Apps environment quota is already
used by an active staging workload. The safe next step is a quota increase or a
separate authorized subscription; the project will not delete or silently share
another workload's environment.

## Documentation highlights

- [Architecture overview](docs/architecture/overview.md)
- [Service-level objectives](docs/sre/service-level-objectives.md)
- [Load and failure testing](docs/operations/load-and-failure-testing.md)
- [Quality and safety observability](docs/ai-observability/quality-and-safety.md)
- [Azure deployment guide](docs/azure/deployment.md)
- [Azure preflight](docs/azure/preflight.md)
- [GitHub OIDC setup](docs/azure/github-oidc.md)
- [Azure teardown and cost control](docs/azure/teardown.md)
- [Project incident and blocker log](docs/operations/project-incident-log.md)
- [Final handoff](docs/portfolio/final-handoff.md)

## Portfolio evidence

Evidence and handoff materials:

- [Project completion report](docs/portfolio/project-completion.md)
- [Final handoff](docs/portfolio/final-handoff.md)
- [Portfolio evidence checklist](docs/portfolio/evidence-checklist.md)
- [Screenshot capture guide](docs/portfolio/screenshot-guide.md)
- [Local evidence collection](docs/portfolio/local-evidence.md)
- [Full Docker/Prometheus evidence files](screenshots/evidence/)
- [API-only evidence files](screenshots/evidence-api-only/)

## Repository structure

```text
app/                    FastAPI service, metrics, middleware, and LLM boundary
prometheus/             Scrape configuration and alert rules
grafana/                Provisioned data source and dashboard
alertmanager/           Alert grouping and routing configuration
tests/                  Unit and integration tests
docs/                   Architecture, SRE, operations, Azure, and portfolio docs
infra/bicep/            Azure infrastructure-as-code
scripts/                Smoke tests, load tests, evidence, Azure helpers
screenshots/            Evidence artifacts and screenshot placeholders
.github/workflows/      CI and Azure deployment workflows
```

## Recruiter / reviewer notes

This project is built to demonstrate hands-on capability across AI DevOps,
observability, SRE, cloud operations, and infrastructure automation. It is not a
toy metrics endpoint; it includes the surrounding operational work expected in
real systems:

- dashboards;
- alert rules;
- runbooks;
- SLOs;
- failure testing;
- CI/CD;
- cloud IaC;
- identity-aware deployment;
- cost and teardown planning;
- incident documentation;
- final handoff.

## Final status

Project implementation: complete.

Remaining external execution:

- optional polished dashboard screenshots for the portfolio gallery;
- real Azure deployment when subscription access, RBAC, quota, OIDC variables,
  and cost approval are ready.
