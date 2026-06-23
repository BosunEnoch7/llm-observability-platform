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

If Docker or Prometheus is unavailable but the FastAPI app is running directly,
collect API-only evidence:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
.\scripts\collect-local-evidence.ps1 -SkipPrometheus
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

In `-SkipPrometheus` mode, the Prometheus target and rule files are not
generated, and `summary.json` sets `prometheus_collected` to `false`.

These files complement screenshots. They should not contain secrets, prompts
from real users, API keys, tenant IDs, subscription IDs, or private data.

## When to use it

Run this collector:

- before capturing final screenshots;
- after dashboard or alert rule changes;
- before a portfolio demo;
- after a local incident or regression fix.

If collection fails, record the issue and treatment in the project incident log.
