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
   .\scripts\smoke-test.ps1
   .\scripts\collect-local-evidence.ps1
   ```

Do not treat this as an application failure unless Docker itself is reachable
and the Compose services still fail.
