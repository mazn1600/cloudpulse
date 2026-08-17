# CloudPulse

CloudPulse is an infrastructure-first learning project. The application is a small workload used to learn Linux, networking, Docker, AWS, CI/CD, Kubernetes, Terraform, monitoring, security, and troubleshooting.

## Milestone 1

```text
Browser → Next.js :3000 → FastAPI :8000 → PostgreSQL :5433
```

The frontend shows a small infrastructure dashboard. FastAPI exposes health, readiness, dashboard, and deployment endpoints. PostgreSQL stores deployment history only.

## Local directories

- `frontend/` — Next.js, TypeScript, and Tailwind CSS
- `backend/` — FastAPI and PostgreSQL access
- `docs/` — architecture and troubleshooting notes

Detailed setup commands are added after both applications exist.
