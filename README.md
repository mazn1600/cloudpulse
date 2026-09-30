# CloudPulse

[![CI](https://github.com/mazn1600/cloudpulse/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/mazn1600/cloudpulse/actions/workflows/ci.yml)

CloudPulse is an infrastructure-first learning project. The application is a small workload used to learn Linux, networking, Docker, AWS, CI/CD, Kubernetes, Terraform, monitoring, security, and troubleshooting.

## Architecture

```text
Browser → Nginx :80 ─┬→ Next.js :3000 → FastAPI :8000 → PostgreSQL
                     └→ FastAPI :8000 (/api/, /health, /ready)
```

The frontend shows a small infrastructure dashboard. FastAPI exposes health, readiness, dashboard, and deployment endpoints. PostgreSQL stores deployment history only. See `docs/architecture.md`.

## Local directories

- `frontend/` — Next.js, TypeScript, and Tailwind CSS
- `backend/` — FastAPI and PostgreSQL access
- `deploy/nginx/` — Nginx reverse proxy config
- `deploy/ssh/` — SSH server hardening config
- `docs/` — architecture and troubleshooting notes

## Prerequisites

Commands are for Windows PowerShell.

```powershell
winget install Python.Python.3.12
winget install OpenJS.NodeJS.LTS
```

Docker Desktop must be running for PostgreSQL. Node.js 24 (see `.node-version`) and Python 3.12 are required.

## Run everything with Docker Compose

```powershell
docker compose up --build
```

Open `http://localhost:3000`. Compose starts PostgreSQL, runs migrations and the seed as a one-off `migrate` job, then starts the backend and frontend once each dependency is healthy. PostgreSQL is only reachable from inside the Compose network. Stop with `Ctrl+C`, or `docker compose down` (add `-v` to also delete the database volume).

## Nginx reverse proxy (Ubuntu on WSL)

Nginx runs in Ubuntu 24.04 on WSL and puts the whole app behind port 80: `/api/`, `/health` and `/ready` go to the backend on `127.0.0.1:8000`, everything else to the frontend on `127.0.0.1:3000`. Start the Compose stack first, then in Ubuntu:

```bash
sudo apt install -y nginx
sudo cp /mnt/c/Users/Gigabyte/Documents/GitHub/cloudpulse/deploy/nginx/cloudpulse.conf /etc/nginx/sites-available/cloudpulse
sudo ln -s /etc/nginx/sites-available/cloudpulse /etc/nginx/sites-enabled/cloudpulse
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
```

Open `http://localhost`. After editing `deploy/nginx/cloudpulse.conf`, copy it again and rerun the last line. A `502 Bad Gateway` means Nginx is up but an upstream app is not running; check `docker compose ps` and `sudo tail /var/log/nginx/error.log`.

## SSH access to the Ubuntu server

Key-only SSH, no passwords and no root login. In Ubuntu:

```bash
sudo apt install -y openssh-server
sudo systemctl enable --now ssh
sudo cp /mnt/c/Users/Gigabyte/Documents/GitHub/cloudpulse/deploy/ssh/00-cloudpulse-hardening.conf /etc/ssh/sshd_config.d/
sudo sshd -t && sudo systemctl reload ssh
```

Your public key (`~/.ssh/id_ed25519.pub` on Windows, created with `ssh-keygen -t ed25519`) must be in `~/.ssh/authorized_keys` on the server before passwords are turned off. Connect from PowerShell with `ssh <user>@localhost`. Keep an existing session open while changing SSH settings, and test the login from a second terminal.

## Local development without containers

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

## Continuous integration

`.github/workflows/ci.yml` runs on every push to `main` and on every pull request. The backend tests and the frontend lint and tests run in parallel; both Docker images are built only if they pass. Make changes on a branch, open a pull request, and merge once the checks are green.

## Operational checks

- API liveness: `curl.exe -i http://localhost:8000/health`
- API readiness: `curl.exe -i http://localhost:8000/ready`
- Interactive API documentation: `http://localhost:8000/docs`
- Troubleshooting guide: `docs/troubleshooting.md`
