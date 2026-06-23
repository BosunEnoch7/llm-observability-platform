# Local evidence collection

This project includes a lightweight evidence collector for portfolio and review
work. It saves machine-readable proof that the local observability stack is
running and producing telemetry.

## Start the stack

```powershell
Copy-Item .env.example .env -ErrorAction SilentlyContinue
docker compose up --build -d
```

Wait until the API and Prometheus are healthy, then run:

```powershell
.\scripts\collect-local-evidence.ps1
```

By default, evidence is written to:

```text
screenshots/evidence/
```

## Files produced

- `health-ready.json` - readiness response from the API.
- `generation-response.json` - sample LLM generation response.
- `feedback-response.json` - sample feedback submission response.
- `metrics.txt` - Prometheus metrics exposed by the API.
- `prometheus-targets.json` - Prometheus scrape target state.
- `prometheus-rules.json` - loaded Prometheus alert/SLO rules.
- `summary.json` - collection timestamp and file index.

These files complement screenshots. They should not contain secrets, prompts
from real users, API keys, tenant IDs, subscription IDs, or private data.

## When to use it

Run this collector:

- before capturing final screenshots;
- after dashboard or alert rule changes;
- before a portfolio demo;
- after a local incident or regression fix.

If collection fails, record the issue and treatment in the project incident log.
