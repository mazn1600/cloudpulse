# CloudPulse Architecture

## Local request path

```text
Browser
  → Next.js on localhost:3000
  → FastAPI on localhost:8000
  → PostgreSQL on localhost:5433 (Docker container cloudpulse-db, internal port 5432)
```

Next.js owns presentation. FastAPI owns the API contract, validation, and database access. PostgreSQL stores deployment history only. The separation lets each process later become an independent container and Kubernetes workload.

The dashboard page is server-rendered on every request, so the **Next.js server** calls FastAPI — the browser never contacts FastAPI or PostgreSQL directly. The API address comes from `NEXT_PUBLIC_API_URL`; it will change when the services move into containers, where `localhost` refers to the container itself.

## Health model

- `GET /health` checks whether the API process can answer HTTP requests. It never touches the database.
- `GET /ready` checks whether the API is ready to serve database-backed traffic. It returns HTTP 503 with `{"status":"not_ready"}` when PostgreSQL is unreachable.
- A process can be alive but not ready; this distinction will later map directly to Kubernetes liveness probes (restart the process) and readiness probes (stop routing traffic to it).

## Failure behavior

| Failure | `/health` | `/ready` | Dashboard |
|---|---|---|---|
| PostgreSQL stopped | 200 | 503 | "API unavailable" page (`/api/v1/deployments` returns 500) |
| FastAPI stopped | connection refused | connection refused | "API unavailable" page |
| Next.js stopped | 200 | 200 | browser shows connection refused |

## Data ownership

Mock CPU, memory, and request values come from FastAPI during Milestone 1. PostgreSQL does not store time-series metrics. Prometheus will own that responsibility in the monitoring phase.

## Configuration

| Service | File | Committed template |
|---|---|---|
| Backend | `backend/.env` | `backend/.env.example` |
| Frontend | `frontend/.env.local` | `frontend/.env.example` |

Real configuration files are ignored by Git. Templates contain local demonstration values only.
