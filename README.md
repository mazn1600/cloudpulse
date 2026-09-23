# CloudPulse

CloudPulse is an infrastructure-first learning project. The application is a small workload used to learn Linux, networking, Docker, AWS, CI/CD, Kubernetes, Terraform, monitoring, security, and troubleshooting.

## Architecture

```text
Browser → Next.js :3000 → FastAPI :8000 → PostgreSQL :5433
```

The frontend shows a small infrastructure dashboard. FastAPI exposes health, readiness, dashboard, and deployment endpoints. PostgreSQL stores deployment history only. See `docs/architecture.md`.

## Local directories

- `frontend/` — Next.js, TypeScript, and Tailwind CSS
- `backend/` — FastAPI and PostgreSQL access
- `docs/` — architecture and troubleshooting notes

## Prerequisites

Commands are for Windows PowerShell.

```powershell
winget install Python.Python.3.12
winget install OpenJS.NodeJS.LTS
```

Docker Desktop must be running for PostgreSQL. Node.js 24 (see `.node-version`) and Python 3.12 are required.

## Local development

Run each long-running server in its own terminal.

### One-time PostgreSQL setup

```powershell
docker run -d --name cloudpulse-db -e POSTGRES_USER=cloudpulse -e POSTGRES_PASSWORD=cloudpulse -e POSTGRES_DB=cloudpulse -p 5433:5432 postgres:16
```

Afterwards, start it with `docker start cloudpulse-db`. The password is a local demonstration value only and must never be reused for cloud or production infrastructure.

### Backend

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
copy .env.example .env
alembic upgrade head
python -m scripts.seed
uvicorn app.main:app --reload --port 8000
```

After the first run, only `.\.venv\Scripts\Activate.ps1` and the `uvicorn` command are needed.

### Frontend

```powershell
cd frontend
copy .env.example .env.local
npm install
npm run dev
```

Open `http://localhost:3000`.

## Tests

```powershell
cd backend; .\.venv\Scripts\Activate.ps1; pytest -q
cd frontend; npm test; npm run lint; npm run build
```

## Operational checks

- API liveness: `curl.exe -i http://localhost:8000/health`
- API readiness: `curl.exe -i http://localhost:8000/ready`
- Interactive API documentation: `http://localhost:8000/docs`
- Troubleshooting guide: `docs/troubleshooting.md`
