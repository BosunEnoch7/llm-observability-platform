# LLM Observability Platform

A production-inspired monitoring and observability platform for Large Language
Model workloads. It combines FastAPI, Prometheus, Grafana, Alertmanager, Docker
Compose, GitHub Actions, and an Azure-focused cloud roadmap.

> **Current phase:** a locally runnable observability stack with simulated and
> Azure OpenAI provider adapters. The simulator makes latency, failures, tokens,
> cost, dashboards, and alerts testable without an API key. Azure infrastructure
> deployment follows in a later phase.

## What this project demonstrates

- AI workload instrumentation and token/cost telemetry
- RED monitoring: request rate, errors, and duration
- Prometheus metric collection, PromQL, and alert rules
- Automatically provisioned Grafana dashboards
- Alertmanager grouping and routing readiness
- Health probes, runbooks, and bounded-cardinality metric labels
- Correlation IDs, structured JSON logs, timeouts, and observable retries
- Containerized local operations and automated CI checks
- A migration path to secure, managed Azure services

## Architecture

```text
Client ---> FastAPI LLM service ---> LLM provider
                    |
                    +-- /metrics <-- Prometheus ---> Grafana
                                         |
                                         +-- alert rules --> Alertmanager
```

The application exposes its own Prometheus endpoint. A separate metrics exporter
is not required for an instrumented Python service; exporters can be introduced
later for external systems that cannot expose metrics themselves.

See [the architecture overview](docs/architecture/overview.md) for design and
metric-label decisions.

## Observability signals

| Signal | Prometheus metric | Purpose |
| --- | --- | --- |
| Request count | `llm_http_requests_total` | Traffic and HTTP outcomes |
| Success/error rate | Derived from request counters | Reliability monitoring |
| HTTP latency | `llm_http_request_duration_seconds` | End-to-end API performance |
| Inference latency | `llm_inference_duration_seconds` | Model/provider performance |
| Inference outcomes | `llm_inference_requests_total` | Model success and failure |
| Provider attempts | `llm_provider_attempts_total` | Success, error, and timeout attempts |
| Provider retries | `llm_provider_retries_total` | Dependency instability |
| Token usage | `llm_tokens_total` | Input/output consumption |
| Estimated cost | `llm_estimated_cost_usd_total` | Cumulative workload cost |
| Service readiness | `llm_service_ready` | Traffic readiness |
| Scrape health | Prometheus `up` | Service reachability |

Prompts, user IDs, and request IDs are deliberately excluded from metric labels
to avoid high cardinality and accidental sensitive-data exposure.

## Repository structure

```text
app/                    FastAPI service, metrics, middleware, and LLM boundary
prometheus/             Scrape configuration and alert rules
grafana/                Provisioned data source and dashboard
alertmanager/           Alert grouping and routing configuration
tests/                  Unit and integration checks
docs/architecture/      Design documentation
docs/runbooks/          Alert response procedures
docs/azure/             Azure target architecture and migration roadmap
scripts/                Local smoke tests
.github/workflows/      Continuous integration
```

## Quick start with Docker Compose

Requirements: Docker Engine with Docker Compose.

```bash
cp .env.example .env
docker compose up --build -d
docker compose ps
```

On PowerShell, copy the environment file with:

```powershell
Copy-Item .env.example .env
```

Open the services:

| Service | URL | Local credentials |
| --- | --- | --- |
| API documentation | <http://localhost:8000/docs> | None |
| Metrics | <http://localhost:8000/metrics> | None |
| Prometheus | <http://localhost:9090> | None |
| Alertmanager | <http://localhost:9093> | None |
| Grafana | <http://localhost:3000> | `admin` / `admin` |

The Grafana password is for local development only and must be replaced by
managed authentication in Azure.

Generate observable traffic:

```bash
curl -X POST http://localhost:8000/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Why does AI observability matter?","max_tokens":64}'
```

PowerShell users can run the complete smoke test:

```powershell
./scripts/smoke-test.ps1
```

Stop the platform with `docker compose down`. Add `--volumes` only when you
intentionally want to remove locally persisted Grafana, Prometheus, and
Alertmanager data.

## Local Python development

```bash
python -m venv .venv
python -m pip install -r requirements.txt
python -m pytest
python -m ruff check app tests
uvicorn app.main:app --reload
```

Activate `.venv` before installing dependencies. Configuration options are
listed in `.env.example`; `.env` and secrets must never be committed.

## Azure OpenAI provider

The simulator remains the default. To select Azure OpenAI, set:

```dotenv
LLM_PROVIDER=azure_openai
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_USE_MANAGED_IDENTITY=true
```

Managed identity is the production default. For local development,
`DefaultAzureCredential` can use an authenticated Azure CLI session. API-key
mode is available as a fallback but keys belong only in the untracked `.env`
file or Azure Key Vault—not source control.

See [Azure OpenAI operations](docs/operations/azure-openai.md) for authentication,
timeouts, retry behavior, pricing configuration, and deployment checks.

## Alerts and runbooks

The alert rules cover service unavailability, generation error rate above 5%,
p95 inference latency above five seconds, and elevated provider retries.
Alertmanager currently uses a safe local placeholder receiver until a real
notification destination is chosen.

- [Service unavailable](docs/runbooks/llm-service-down.md)
- [High error rate](docs/runbooks/high-error-rate.md)
- [High latency](docs/runbooks/high-latency.md)

## Azure direction

The intended production path uses Azure Container Registry, Azure Container
Apps (or AKS when justified), Azure OpenAI, Key Vault, managed identity, Azure
Monitor managed Prometheus, Azure Managed Grafana, and GitHub Actions OIDC.
Infrastructure-as-code will be added in a later phase.

See the [Azure deployment roadmap](docs/azure/roadmap.md).

## Roadmap

1. Core API, metrics, dashboards, alerting, tests, and CI
2. Azure OpenAI adapter, retries, timeouts, secure configuration, and JSON logs
3. Distributed traces and OpenTelemetry
4. SLOs, multi-window burn-rate alerts, load testing, and failure injection
5. Azure infrastructure-as-code, workload identity, deployment, and operations
