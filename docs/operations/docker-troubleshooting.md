# Docker troubleshooting

## Docker API permission denied on Windows

Symptom:

```text
permission denied while trying to connect to the docker API at npipe:////./pipe/docker_engine
```

Impact:

- `docker compose up`
- `docker compose ps`
- local evidence collection that depends on running services

Common causes:

- Docker Desktop is not running.
- The current terminal/user cannot access the Docker Engine named pipe.
- Docker Desktop is still starting.
- Windows/OneDrive/sandbox policy is restricting access.

Treatment:

1. Start Docker Desktop.
2. Wait until Docker says it is running.
3. Open a fresh PowerShell terminal.
4. Run:

   ```powershell
   docker version
   docker compose ps
   ```

5. If permission is still denied, run the terminal as the same Windows user that
   owns Docker Desktop, or restart Docker Desktop.
6. Retry:

   ```powershell
   docker compose up --build -d
   powershell -ExecutionPolicy Bypass -File .\scripts\smoke-test.ps1
   powershell -ExecutionPolicy Bypass -File .\scripts\collect-local-evidence.ps1
   ```

Do not treat this as an application failure unless Docker itself is reachable
and the Compose services still fail.

If Docker remains unavailable, run FastAPI directly and collect API-only
evidence:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
powershell -ExecutionPolicy Bypass -File .\scripts\collect-local-evidence.ps1 -SkipPrometheus
```

## Package downloads fail during image build

Symptoms include DNS timeouts for `files.pythonhosted.org` or a misleading
`No matching distribution found` message after package metadata downloads stall.

Treatment:

1. Confirm the host has internet access.
2. Retry the cached build.
3. If Docker's internal DNS remains unstable, build the application image with:

   ```powershell
   docker build --network=host -t llm-observability-platform-llm-service:latest .
   docker compose up -d --no-build
   ```

The runtime image installs only `requirements.txt`. Test, coverage, and lint
tools live in `requirements-dev.txt`, keeping production builds smaller and
reducing their dependency surface.
