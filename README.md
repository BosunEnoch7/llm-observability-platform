# LLM Observability Platform

A production-inspired monitoring and observability platform for Large Language
Model workloads. It combines FastAPI, Prometheus, Grafana, Alertmanager, Docker
Compose, GitHub Actions, and Azure-ready infrastructure-as-code.

> **Status:** local/repository implementation complete. The simulator makes
> latency, failures, tokens, cost, dashboards, and alerts testable without an
> API key. Real Azure deployment is gated on authorized subscription access,
> GitHub OIDC variables, quota, and cost approval.

## What this project demonstrates

- AI workload instrumentation and token/cost telemetry
- RED monitoring: request rate, errors, and duration
- Prometheus metric collection, PromQL, and alert rules
- Automatically provisioned Grafana dashboards
- Alertmanager grouping and routing readiness
- Health probes, runbooks, and bounded-cardinality metric labels
- Correlation IDs, structured JSON logs, timeouts, and observable retries
- Optional OTLP distributed tracing with log/trace correlation
- A 99% availability SLO with multi-window error-budget alerts
- Aggregate quality feedback, safety events, and prompt-version telemetry
- Containerized local operations and automated CI checks
- Azure-ready Bicep infrastructure and GitHub OIDC deployment workflow
- Portfolio evidence, runbooks, and incident/blocker tracking

## Architecture

```text
Client ---> FastAPI LLM service ---> LLM provider
                    |
                    +-- /metrics <-- Prometheus ---> Grafana
                    |                    |
                    |                    +-- alert rules --> Alertmanager
                    |
                    +-- OTLP traces -----------------------> Jaeger
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
| Prompt releases | `llm_prompt_version_requests_total` | Version adoption and comparison |
| Safety findings | `llm_safety_events_total` | Bounded category/action events |
| Quality rating | `llm_quality_rating` | Aggregate one-to-five user ratings |
| User feedback | `llm_feedback_total` | Helpful/negative feedback ratios |
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
docs/ai-observability/  Quality and safety signal design
docs/runbooks/          Alert response procedures
docs/operations/        Tracing, testing, and project incident history
docs/portfolio/         Completion report and evidence checklist
docs/azure/             Azure target architecture and migration roadmap
infra/bicep/            Azure foundation and Container Apps infrastructure
screenshots/            Portfolio screenshots and validation evidence
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
| Jaeger traces | <http://localhost:16686> | None |

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

## Distributed tracing

Set `OTEL_ENABLED=true` to instrument FastAPI requests and provider calls. Traces
are exported over OTLP to the local Jaeger service, while structured logs gain
the active `trace_id` and `span_id`. Prompt content is deliberately excluded
from trace attributes.

See [tracing operations](docs/operations/tracing.md) for local usage and the
Azure Monitor exporter migration path.

## Alerts and runbooks

The alert rules cover service unavailability, generation error rate above 5%,
p95 inference latency above five seconds, and elevated provider retries.
Alertmanager currently uses a safe local placeholder receiver until a real
notification destination is chosen.

- [Service unavailable](docs/runbooks/llm-service-down.md)
- [High error rate](docs/runbooks/high-error-rate.md)
- [High latency](docs/runbooks/high-latency.md)
- [Availability error-budget burn](docs/runbooks/availability-slo-burn.md)

Project build blockers, validation issues, and their treatments are tracked in
the [project incident and blocker log](docs/operations/project-incident-log.md).

The availability objective and burn-rate rationale are documented in
[service-level objectives](docs/sre/service-level-objectives.md).

## Load and failure testing

Run `python scripts/load_test.py --duration 60 --concurrency 5` for controlled
local traffic. The `docker-compose.failure.yml` overlay injects latency and a
25% simulated provider failure rate to exercise retries, traces, dashboards,
and SLO alerts. Follow the [load and failure testing guide](docs/operations/load-and-failure-testing.md).

## Quality and safety signals

Generation responses include an `inference_id` and the configured prompt
version. Clients can submit bounded aggregate feedback to `POST /v1/feedback`.
Safety evaluation defaults to monitor mode and can be disabled or changed to
enforcement with `SAFETY_MODE`.

The local safety rules are intentionally small and exist to exercise telemetry
and operational workflows. They are not a substitute for Azure AI Content
Safety, policy governance, durable audit storage, and human review. See
[quality and safety observability](docs/ai-observability/quality-and-safety.md).

## Azure direction

The intended production path uses Azure Container Registry, Azure Container
Apps (or AKS when justified), Azure OpenAI, Key Vault, managed identity, Azure
Monitor managed Prometheus, Azure Managed Grafana, and GitHub Actions OIDC.
Infrastructure-as-code is now included for the first Azure deployment path.

The first Bicep deployment and GitHub OIDC workflow are now included. Review the
[Azure preflight guide](docs/azure/preflight.md) and
[GitHub OIDC setup](docs/azure/github-oidc.md), then follow the
[Azure deployment guide](docs/azure/deployment.md) before provisioning
resources. Review [Azure teardown and cost control](docs/azure/teardown.md)
before cloud tests. Use the [Azure roadmap](docs/azure/roadmap.md) for the
managed-cloud promotion path.

## Portfolio and completion evidence

- [Project completion report](docs/portfolio/project-completion.md)
- [Portfolio evidence checklist](docs/portfolio/evidence-checklist.md)
- [Screenshot capture guide](docs/portfolio/screenshot-guide.md)
- [Local evidence collection](docs/portfolio/local-evidence.md)
- [Project incident and blocker log](docs/operations/project-incident-log.md)
- [Docker troubleshooting](docs/operations/docker-troubleshooting.md)

## Roadmap

1. Core API, metrics, dashboards, alerting, tests, and CI - complete
2. Azure OpenAI adapter, retries, timeouts, secure configuration, and JSON logs - complete
3. Distributed traces, SLOs, burn-rate alerts, load testing, and failure injection - complete
4. Quality feedback, safety signals, and prompt-version telemetry - complete
5. Azure IaC, deployment workflow, incident log, and portfolio evidence - complete
6. Azure preflight - in progress
7. Real Azure deployment execution - pending authorized cloud access and cost approval
