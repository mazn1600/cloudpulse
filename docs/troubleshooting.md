# CloudPulse Troubleshooting

Commands are for Windows PowerShell. Investigate before changing code or configuration: read the terminal logs, check what is actually running, then act.

## Read the error you are seeing

| Symptom | Meaning | Look at |
|---|---|---|
| Browser: `ERR_CONNECTION_REFUSED` | Nothing is listening on that port | Is the process running? |
| HTTP 500 Internal Server Error | The server crashed while handling the request | Backend terminal traceback (read the last line first) |
| HTTP 503 from `/ready` | API is alive but PostgreSQL is unreachable | Database container |
| Dashboard shows "API unavailable" | Next.js could not get data from FastAPI | FastAPI terminal, then `/ready` |

## Check listening ports

```powershell
Get-NetTCPConnection -State Listen -LocalPort 3000, 8000, 5433 -ErrorAction SilentlyContinue |
  Select-Object LocalAddress, LocalPort, OwningProcess
```

A missing port means no process is listening on it. Find which program owns a port:

```powershell
Get-Process -Id (Get-NetTCPConnection -State Listen -LocalPort 8000).OwningProcess
```

## Check the API

In Windows PowerShell 5.1, `curl` is an alias for `Invoke-WebRequest`. Use `curl.exe` for real curl:

```powershell
curl.exe -i http://localhost:8000/health
curl.exe -i http://localhost:8000/ready
```

`/health` should return HTTP 200 whenever FastAPI is running. `/ready` returns HTTP 503 when PostgreSQL is unavailable.

## Check PostgreSQL

```powershell
docker ps -a --filter name=cloudpulse-db
docker exec cloudpulse-db pg_isready -U cloudpulse
docker exec cloudpulse-db psql -U cloudpulse -c "SELECT * FROM deployments;"
docker logs --tail 50 cloudpulse-db
```

If Docker reports `failed to connect to the docker API`, Docker Desktop is not running — start it and wait for "Engine running".

## Common setup problems

| Problem | Cause | Fix |
|---|---|---|
| `fatal: not a git repository` | Terminal is not inside the project folder | `cd` into `cloudpulse` first |
| `pip install` rejects the Python version | Project requires Python 3.12 | `py -3.12 -m venv .venv` |
| `Activate.ps1 cannot be loaded` | PowerShell script execution disabled | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `python --version` is not 3.12 | Virtual environment not activated | `.\.venv\Scripts\Activate.ps1` |
| Seed script prints nothing | Success is silent | Check `$LASTEXITCODE` is `0`, or query the table |
| API stopped after starting the database | `Ctrl+C` in the uvicorn terminal | Run servers and ad-hoc commands in separate terminals |
| `LF will be replaced by CRLF` | Git line-ending conversion on Windows | Warning only; no action needed |
