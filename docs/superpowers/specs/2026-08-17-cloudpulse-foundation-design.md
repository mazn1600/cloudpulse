# CloudPulse Foundation Design

**Date:** 2026-08-17
**Milestone:** Phase 1 — local application foundation

## Purpose

CloudPulse is an infrastructure-first learning project. The application is intentionally small: it gives us one realistic workload to run, package, deploy, observe, secure, and troubleshoot while learning Linux, networking, Docker, AWS, CI/CD, Kubernetes, Terraform, and monitoring.

The first milestone proves only that a browser, frontend, API, and database can communicate locally. It does not introduce infrastructure tooling prematurely.

## Architecture

```text
Browser
  |
  v
Next.js frontend (localhost:3000)
  |
  | HTTP/JSON
  v
FastAPI backend (localhost:8000)
  |
  | SQL
  v
PostgreSQL (localhost:5432)
```

The repository is a monorepo with three clear areas:

```text
cloudpulse/
├── frontend/   # Next.js, TypeScript, Tailwind CSS
├── backend/    # FastAPI, Python 3.12, database access and API tests
└── docs/       # Architecture, setup, learning notes and troubleshooting
```

The frontend never connects directly to PostgreSQL. It requests data from FastAPI, which owns validation and database access. This boundary remains valid when the services later move into containers and Kubernetes.

## Milestone 1 Behavior

The frontend provides one responsive dashboard containing:

- overall CloudPulse status;
- frontend, API, and database service status;
- mocked CPU, memory, request, and infrastructure values;
- recent deployments loaded from the backend;
- a visible unavailable state when the API cannot be reached.

The backend provides:

- `GET /health` for process liveness without a database dependency;
- `GET /ready` for readiness, including a PostgreSQL connectivity check;
- `GET /api/v1/dashboard` for typed mock dashboard metrics;
- `GET /api/v1/deployments` for deployment history stored in PostgreSQL.

PostgreSQL stores only deployment records in this milestone. Metrics and logs are not stored because later monitoring systems will own that data.

## Configuration and Security

- Node.js 24 LTS runs the frontend; Python 3.12 runs the backend.
- Local ports are `3000` for Next.js, `8000` for FastAPI, and `5432` for PostgreSQL.
- The frontend receives the API base URL through an environment variable.
- The backend receives its database connection string through `DATABASE_URL`.
- Example environment files contain safe placeholders only; real passwords and credentials are ignored by Git.
- FastAPI CORS allows only the local frontend origin during this milestone.
- No AWS credentials or paid AWS resources are used.

## Failure Handling and Troubleshooting

- The liveness endpoint remains useful when PostgreSQL is unavailable.
- The readiness endpoint reports an unavailable dependency without exposing credentials or internal stack traces.
- The frontend distinguishes loading, successful, empty, and API-unavailable states.
- Setup documentation includes commands for checking processes, ports, HTTP responses, backend logs, and PostgreSQL connectivity.
- We investigate failures before changing code or configuration.

## Testing and Acceptance Criteria

The milestone is complete when:

1. The frontend and backend start independently on their documented ports.
2. Backend tests verify health, readiness failure handling, dashboard response shape, and deployment retrieval.
3. Frontend tests verify dashboard rendering and the API-unavailable state.
4. PostgreSQL contains the minimal deployment-history schema and the API can read it.
5. A browser can load the dashboard and display data returned by FastAPI.
6. No secret or generated dependency directory is tracked by Git.
7. The README explains local startup, architecture, tests, and common troubleshooting commands.

## Explicitly Deferred

Docker, Linux server deployment, Nginx, AWS resources, GitHub Actions, Kubernetes, Terraform, Prometheus, Grafana, authentication, microservices, Redis, Kafka, and production logging are outside this milestone. Each will be introduced in its own learning stage after the local foundation is understood and verified.
