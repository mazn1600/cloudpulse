# CloudPulse Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first local CloudPulse milestone: a Next.js dashboard that reads operational data from FastAPI, with PostgreSQL used only for deployment history.

**Architecture:** The browser talks only to the Next.js frontend on port 3000. Next.js calls the FastAPI HTTP/JSON interface on port 8000; FastAPI owns validation and PostgreSQL access on port 5433. Liveness remains independent of PostgreSQL, while readiness reports database availability.

**Tech Stack:** Node.js 24 LTS, Next.js 16.3.1, React 19.2.8, TypeScript, Tailwind CSS 4.3.3, Python 3.12, FastAPI 0.141.1, SQLAlchemy 2.0.52, Alembic 1.19.1, PostgreSQL 18, pytest 9.1.1, Vitest 4.1.10.

## Global Constraints

- Node.js 24 LTS runs the frontend; Python 3.12 runs the backend.
- Local ports are `3000` for Next.js, `8000` for FastAPI, and `5433` for PostgreSQL because an existing PostgreSQL installation owns `5432` on this machine.
- PostgreSQL stores deployment history only; dashboard metrics remain deterministic mock data.
- The browser and frontend never connect directly to PostgreSQL.
- Secrets stay in ignored `.env` files; only safe `.env.example` files are committed.
- CORS allows only `http://localhost:3000` during this milestone.
- Docker, AWS resources, CI/CD, Kubernetes, Terraform, Prometheus, Grafana, authentication, and production logging remain deferred.

## File Map

- Root: `.node-version`, `.gitignore`, and `README.md` define the local contract and repository hygiene.
- `backend/app/main.py` composes FastAPI; focused router, schema, database, model, and repository modules own one responsibility each.
- `backend/alembic/` owns the deployment-history schema migration; `backend/scripts/seed.py` creates one repeatable demonstration record.
- `frontend/src/lib/` owns the API contract and fetch logic; `frontend/src/components/` renders data and failure states; `frontend/src/app/page.tsx` coordinates them.
- `docs/architecture.md` and `docs/troubleshooting.md` preserve the infrastructure mental model and diagnostic commands.

---

### Task 1: Repository Foundation

**Files:**
- Create: `.node-version`
- Create: `.gitignore`
- Create: `README.md`

**Interfaces:**
- Produces: Node major version `24`, repository ignore rules, and the root commands used by every later task.

- [ ] **Step 1: Pin Node and protect generated or secret files**

Create `.node-version`:

```text
24
```

Create `.gitignore`:

```gitignore
.DS_Store
.env
.env.*
!.env.example

frontend/node_modules/
frontend/.next/
frontend/coverage/

backend/.venv/
backend/__pycache__/
backend/.pytest_cache/
backend/.coverage
backend/htmlcov/
*.py[cod]
*.egg-info/
```

- [ ] **Step 2: Write the initial project entrypoint**

Create `README.md`:

````markdown
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
````

- [ ] **Step 3: Verify repository hygiene**

Run:

```bash
mkdir -p frontend/node_modules backend/.venv
touch .env frontend/.env backend/.env
git status --short --ignored
rmdir frontend/node_modules backend/.venv
rm .env frontend/.env backend/.env
```

Expected: all three `.env` paths, `frontend/node_modules/`, and `backend/.venv/` appear with `!!`; none appears as an untracked `??` path.

- [ ] **Step 4: Commit**

```bash
git add .node-version .gitignore README.md
git commit -m "chore: establish project foundation"
```

---

### Task 2: FastAPI Liveness and Mock Dashboard

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/.env.example`
- Create: `backend/app/__init__.py`
- Create: `backend/app/settings.py`
- Create: `backend/app/schemas.py`
- Create: `backend/app/routers/__init__.py`
- Create: `backend/app/routers/health.py`
- Create: `backend/app/routers/dashboard.py`
- Create: `backend/app/main.py`
- Create: `backend/tests/test_health.py`
- Create: `backend/tests/test_dashboard.py`

**Interfaces:**
- Produces: `GET /health -> HealthResponse` and `GET /api/v1/dashboard -> DashboardResponse`.
- `HealthResponse`: `{ "status": "ok", "service": "cloudpulse-api" }`.
- `DashboardResponse`: `{ "status", "metrics", "services" }` with snake_case JSON fields.

- [ ] **Step 1: Create the Python package and install dependencies**

Create `backend/pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=75"]
build-backend = "setuptools.build_meta"

[project]
name = "cloudpulse-api"
version = "0.1.0"
requires-python = ">=3.12,<3.13"
dependencies = [
  "alembic==1.19.1",
  "asyncpg==0.31.0",
  "fastapi==0.141.1",
  "pydantic-settings==2.15.0",
  "sqlalchemy[asyncio]==2.0.52",
  "uvicorn[standard]==0.52.3",
]

[project.optional-dependencies]
dev = [
  "httpx2==2.10.0",
  "pytest==9.1.1",
  "pytest-asyncio==1.4.0",
]

[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
asyncio_mode = "auto"

[tool.setuptools.packages.find]
include = ["app*"]
```

Create `backend/.env.example`:

```dotenv
DATABASE_URL=postgresql+asyncpg://cloudpulse:cloudpulse@localhost:5433/cloudpulse
FRONTEND_ORIGIN=http://localhost:3000
```

Run:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

Expected: installation succeeds and `python -c "import fastapi; print(fastapi.__version__)"` prints `0.141.1`.

- [ ] **Step 2: Write failing endpoint tests**

Create empty package markers at `backend/app/__init__.py` and `backend/app/routers/__init__.py`.

Create `backend/tests/test_health.py`:

```python
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_does_not_require_database() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "cloudpulse-api"}
```

Create `backend/tests/test_dashboard.py`:

```python
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_dashboard_returns_typed_mock_metrics() -> None:
    response = client.get("/api/v1/dashboard")

    assert response.status_code == 200
    assert response.json() == {
        "status": "operational",
        "metrics": {
            "cpu_percent": 38.4,
            "memory_percent": 62.1,
            "requests_per_minute": 128,
        },
        "services": [
            {"name": "frontend", "status": "operational"},
            {"name": "api", "status": "operational"},
            {"name": "database", "status": "unknown"},
        ],
    }
```

- [ ] **Step 3: Run tests to verify they fail**

Run:

```bash
cd backend
source .venv/bin/activate
pytest -q
```

Expected: collection fails because `app.main` does not exist.

- [ ] **Step 4: Implement settings, schemas, routers, and application composition**

Create `backend/app/settings.py`:

```python
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://cloudpulse:cloudpulse@localhost:5433/cloudpulse"
    frontend_origin: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

Create `backend/app/schemas.py`:

```python
from typing import Literal

from pydantic import BaseModel


ServiceStatus = Literal["operational", "degraded", "unknown"]


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str


class MetricSnapshot(BaseModel):
    cpu_percent: float
    memory_percent: float
    requests_per_minute: int


class ServiceSnapshot(BaseModel):
    name: str
    status: ServiceStatus


class DashboardResponse(BaseModel):
    status: ServiceStatus
    metrics: MetricSnapshot
    services: list[ServiceSnapshot]
```

Create `backend/app/routers/health.py`:

```python
from fastapi import APIRouter

from app.schemas import HealthResponse


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", service="cloudpulse-api")
```

Create `backend/app/routers/dashboard.py`:

```python
from fastapi import APIRouter

from app.schemas import DashboardResponse, MetricSnapshot, ServiceSnapshot


router = APIRouter(prefix="/api/v1", tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardResponse)
async def dashboard() -> DashboardResponse:
    return DashboardResponse(
        status="operational",
        metrics=MetricSnapshot(
            cpu_percent=38.4,
            memory_percent=62.1,
            requests_per_minute=128,
        ),
        services=[
            ServiceSnapshot(name="frontend", status="operational"),
            ServiceSnapshot(name="api", status="operational"),
            ServiceSnapshot(name="database", status="unknown"),
        ],
    )
```

Create `backend/app/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import dashboard, health
from app.settings import get_settings


settings = get_settings()
app = FastAPI(title="CloudPulse API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)
app.include_router(health.router)
app.include_router(dashboard.router)
```

- [ ] **Step 5: Run tests and application smoke check**

```bash
cd backend
source .venv/bin/activate
pytest -q
uvicorn app.main:app --port 8000
```

In a second terminal run:

```bash
curl -i http://localhost:8000/health
curl -s http://localhost:8000/api/v1/dashboard | python3 -m json.tool
```

Expected: tests pass; `/health` returns HTTP 200; dashboard JSON matches the test. Stop Uvicorn with `Control+C`.

- [ ] **Step 6: Commit**

```bash
git add backend
git commit -m "feat: add CloudPulse health and dashboard API"
```

---

### Task 3: PostgreSQL Readiness and Deployment History

**Files:**
- Create: `backend/app/database.py`
- Create: `backend/app/models.py`
- Create: `backend/app/repositories/__init__.py`
- Create: `backend/app/repositories/deployments.py`
- Create: `backend/app/routers/deployments.py`
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`
- Create: `backend/alembic/versions/20260817_01_create_deployments.py`
- Create: `backend/scripts/seed.py`
- Create: `backend/tests/test_readiness.py`
- Create: `backend/tests/test_deployments.py`
- Modify: `backend/app/schemas.py`
- Modify: `backend/app/routers/health.py`
- Modify: `backend/app/main.py`

**Interfaces:**
- Produces: `GET /ready -> ReadinessResponse`, returning HTTP 200 for database `up` and HTTP 503 for database `down`.
- Produces: `GET /api/v1/deployments -> list[DeploymentResponse]`, newest first and limited to ten records.
- Consumes: `Settings.database_url` and an async SQLAlchemy session.

- [ ] **Step 1: Install and start PostgreSQL locally**

```bash
brew install postgresql@18
brew services stop postgresql@18
sed -i '' 's/^#port = 5432/port = 5433/' /opt/homebrew/var/postgresql@18/postgresql.conf
brew services start postgresql@18
/opt/homebrew/opt/postgresql@18/bin/pg_isready -p 5433
```

Expected: `pg_isready` reports `accepting connections` on port 5433. The Homebrew cluster uses 5433 so the pre-existing `/Library/PostgreSQL/18` server can retain port 5432.

Create the local role and database:

```bash
/opt/homebrew/opt/postgresql@18/bin/createuser -p 5433 --login cloudpulse
/opt/homebrew/opt/postgresql@18/bin/createdb -p 5433 --owner=cloudpulse cloudpulse
/opt/homebrew/opt/postgresql@18/bin/psql -p 5433 -d postgres -c "ALTER ROLE cloudpulse WITH PASSWORD 'cloudpulse';"
```

Expected: role and database creation succeeds; the password is local-only and must not be reused outside development.

- [ ] **Step 2: Write failing readiness and deployment tests**

Create `backend/tests/test_readiness.py`:

```python
from collections.abc import AsyncIterator

from fastapi.testclient import TestClient

from app.database import get_database_status
from app.main import app


client = TestClient(app)


async def database_up() -> AsyncIterator[str]:
    yield "up"


async def database_down() -> AsyncIterator[str]:
    yield "down"


def test_readiness_is_ready_when_database_is_up() -> None:
    app.dependency_overrides[get_database_status] = database_up
    response = client.get("/ready")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"status": "ready", "dependencies": {"database": "up"}}


def test_readiness_is_unavailable_when_database_is_down() -> None:
    app.dependency_overrides[get_database_status] = database_down
    response = client.get("/ready")
    app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json() == {
        "status": "not_ready",
        "dependencies": {"database": "down"},
    }
```

Create `backend/tests/test_deployments.py`:

```python
from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.main import app
from app.repositories.deployments import get_recent_deployments
from app.schemas import DeploymentResponse


client = TestClient(app)


async def fake_deployments() -> list[DeploymentResponse]:
    return [
        DeploymentResponse(
            id=1,
            version="v0.1.0",
            environment="local",
            status="successful",
            deployed_at=datetime(2026, 8, 17, 12, 0, tzinfo=UTC),
        )
    ]


def test_deployments_returns_recent_history() -> None:
    app.dependency_overrides[get_recent_deployments] = fake_deployments
    response = client.get("/api/v1/deployments")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "version": "v0.1.0",
            "environment": "local",
            "status": "successful",
            "deployed_at": "2026-08-17T12:00:00Z",
        }
    ]
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
cd backend
source .venv/bin/activate
pytest tests/test_readiness.py tests/test_deployments.py -q
```

Expected: collection fails because the database and deployment modules do not exist.

- [ ] **Step 4: Implement database dependencies and models**

Create `backend/app/database.py`:

```python
from collections.abc import AsyncIterator
from typing import Annotated, Literal

from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.settings import get_settings


DatabaseStatus = Literal["up", "down"]

engine = create_async_engine(
    get_settings().database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=5,
)
session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_database_status() -> DatabaseStatus:
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return "up"
    except SQLAlchemyError:
        return "down"


DatabaseStatusDep = Annotated[DatabaseStatus, Depends(get_database_status)]
```

Create `backend/app/models.py`:

```python
from datetime import datetime

from sqlalchemy import BigInteger, CheckConstraint, DateTime, Identity, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Deployment(Base):
    __tablename__ = "deployments"
    __table_args__ = (
        CheckConstraint(
            "status IN ('successful', 'failed', 'running')",
            name="deployments_status_check",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    version: Mapped[str] = mapped_column(Text)
    environment: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text)
    deployed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
```

Replace `backend/app/schemas.py` with:

```python
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


ServiceStatus = Literal["operational", "degraded", "unknown"]


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str


class MetricSnapshot(BaseModel):
    cpu_percent: float
    memory_percent: float
    requests_per_minute: int


class ServiceSnapshot(BaseModel):
    name: str
    status: ServiceStatus


class DashboardResponse(BaseModel):
    status: ServiceStatus
    metrics: MetricSnapshot
    services: list[ServiceSnapshot]


class DependencyStatus(BaseModel):
    database: Literal["up", "down"]


class ReadinessResponse(BaseModel):
    status: Literal["ready", "not_ready"]
    dependencies: DependencyStatus


class DeploymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    version: str
    environment: str
    status: Literal["successful", "failed", "running"]
    deployed_at: datetime
```

- [ ] **Step 5: Implement readiness and deployment routing**

Replace `backend/app/routers/health.py` with:

```python
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.database import get_database_status
from app.schemas import DependencyStatus, HealthResponse, ReadinessResponse


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", service="cloudpulse-api")


@router.get("/ready", response_model=ReadinessResponse)
async def readiness(
    database: Annotated[str, Depends(get_database_status)],
) -> ReadinessResponse | JSONResponse:
    if database == "down":
        response = ReadinessResponse(
            status="not_ready", dependencies=DependencyStatus(database="down")
        )
        return JSONResponse(status_code=503, content=response.model_dump())

    return ReadinessResponse(
        status="ready", dependencies=DependencyStatus(database="up")
    )
```

Create empty `backend/app/repositories/__init__.py`.

Create `backend/app/repositories/deployments.py`:

```python
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Deployment
from app.schemas import DeploymentResponse


async def get_recent_deployments(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[DeploymentResponse]:
    statement = select(Deployment).order_by(Deployment.deployed_at.desc()).limit(10)
    result = await session.scalars(statement)
    return [DeploymentResponse.model_validate(item) for item in result.all()]
```

Create `backend/app/routers/deployments.py`:

```python
from typing import Annotated

from fastapi import APIRouter, Depends

from app.repositories.deployments import get_recent_deployments
from app.schemas import DeploymentResponse


router = APIRouter(prefix="/api/v1", tags=["deployments"])


@router.get("/deployments", response_model=list[DeploymentResponse])
async def deployments(
    items: Annotated[list[DeploymentResponse], Depends(get_recent_deployments)],
) -> list[DeploymentResponse]:
    return items
```

Replace `backend/app/main.py` with:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import dashboard, deployments, health
from app.settings import get_settings


settings = get_settings()
app = FastAPI(title="CloudPulse API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)
app.include_router(health.router)
app.include_router(dashboard.router)
app.include_router(deployments.router)
```

- [ ] **Step 6: Add the schema migration**

Create `backend/alembic.ini`:

```ini
[alembic]
script_location = alembic
prepend_sys_path = .

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

Create `backend/alembic/env.py`:

```python
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.models import Base
from app.settings import get_settings


config = context.config
config.set_main_option(
    "sqlalchemy.url", get_settings().database_url.replace("+asyncpg", "+psycopg")
)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

Replace `backend/pyproject.toml` with the complete dependency set:

```toml
[build-system]
requires = ["setuptools>=75"]
build-backend = "setuptools.build_meta"

[project]
name = "cloudpulse-api"
version = "0.1.0"
requires-python = ">=3.12,<3.13"
dependencies = [
  "alembic==1.19.1",
  "asyncpg==0.31.0",
  "fastapi==0.141.1",
  "psycopg[binary]==3.3.4",
  "pydantic-settings==2.15.0",
  "sqlalchemy[asyncio]==2.0.52",
  "uvicorn[standard]==0.52.3",
]

[project.optional-dependencies]
dev = [
  "httpx2==2.10.0",
  "pytest==9.1.1",
  "pytest-asyncio==1.4.0",
]

[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
asyncio_mode = "auto"

[tool.setuptools.packages.find]
include = ["app*"]
```

Run `python -m pip install -e '.[dev]'`. Alembic uses the synchronous Psycopg 3 driver while the application uses `asyncpg`.

Create `backend/alembic/versions/20260817_01_create_deployments.py`:

```python
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20260817_01"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "deployments",
        sa.Column(
            "id",
            sa.BigInteger(),
            sa.Identity(always=True),
            primary_key=True,
        ),
        sa.Column("version", sa.Text(), nullable=False),
        sa.Column("environment", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column(
            "deployed_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('successful', 'failed', 'running')",
            name="deployments_status_check",
        ),
    )
    op.create_index(
        "ix_deployments_deployed_at",
        "deployments",
        ["deployed_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_deployments_deployed_at", table_name="deployments")
    op.drop_table("deployments")
```

- [ ] **Step 7: Add repeatable local seed data**

Create `backend/scripts/seed.py`:

```python
import asyncio

from sqlalchemy import func, select

from app.database import session_factory
from app.models import Deployment


async def seed() -> None:
    async with session_factory() as session:
        count = await session.scalar(select(func.count()).select_from(Deployment))
        if count == 0:
            session.add(
                Deployment(
                    version="v0.1.0",
                    environment="local",
                    status="successful",
                )
            )
            await session.commit()


if __name__ == "__main__":
    asyncio.run(seed())
```

- [ ] **Step 8: Run tests, migrate, seed, and verify**

```bash
cd backend
source .venv/bin/activate
pytest -q
alembic upgrade head
python -m scripts.seed
uvicorn app.main:app --port 8000
```

In a second terminal:

```bash
curl -i http://localhost:8000/ready
curl -s http://localhost:8000/api/v1/deployments | python3 -m json.tool
```

Expected: tests pass, readiness returns HTTP 200 with database `up`, and deployments returns the seeded `v0.1.0` record. Stop Uvicorn with `Control+C`.

- [ ] **Step 9: Commit**

```bash
git add backend
git commit -m "feat: add database readiness and deployment history"
```

---

### Task 4: Next.js Dashboard and API Client

**Files:**
- Create: `frontend/` with `create-next-app`
- Create: `frontend/.env.example`
- Create: `frontend/src/lib/types.ts`
- Create: `frontend/src/lib/api.ts`
- Create: `frontend/src/components/dashboard.tsx`
- Create: `frontend/src/components/api-unavailable.tsx`
- Create: `frontend/src/app/loading.tsx`
- Modify: `frontend/src/app/page.tsx`
- Modify: `frontend/src/app/layout.tsx`
- Modify: `frontend/src/app/globals.css`

**Interfaces:**
- Consumes: `GET /api/v1/dashboard` and `GET /api/v1/deployments` from Task 2 and Task 3.
- Produces: `getDashboard(): Promise<DashboardResponse>` and `getDeployments(): Promise<Deployment[]>`.
- Produces: `<Dashboard dashboard deployments />` and `<ApiUnavailable />` UI boundaries.

- [ ] **Step 1: Scaffold the frontend and add test dependencies**

From the repository root:

```bash
source "$HOME/.bashrc"
fnm use 24
npx create-next-app@16.3.1 frontend --typescript --tailwind --eslint --app --src-dir --import-alias '@/*' --use-npm --yes
cd frontend
npm install --save-dev vitest@4.1.10 jsdom@30.0.1 @vitejs/plugin-react@6.0.5 @testing-library/react@16.3.2 @testing-library/jest-dom@7.0.1
```

Expected: the application scaffold succeeds and `npm run build` passes before customization.

- [ ] **Step 2: Define the API contract and fetch client**

Create `frontend/.env.example`:

```dotenv
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Create `frontend/src/lib/types.ts`:

```typescript
export type ServiceStatus = "operational" | "degraded" | "unknown";

export interface MetricSnapshot {
  cpu_percent: number;
  memory_percent: number;
  requests_per_minute: number;
}

export interface ServiceSnapshot {
  name: string;
  status: ServiceStatus;
}

export interface DashboardResponse {
  status: ServiceStatus;
  metrics: MetricSnapshot;
  services: ServiceSnapshot[];
}

export interface Deployment {
  id: number;
  version: string;
  environment: string;
  status: "successful" | "failed" | "running";
  deployed_at: string;
}
```

Create `frontend/src/lib/api.ts`:

```typescript
import type { DashboardResponse, Deployment } from "@/lib/types";

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${apiUrl}${path}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`CloudPulse API returned ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function getDashboard(): Promise<DashboardResponse> {
  return getJson<DashboardResponse>("/api/v1/dashboard");
}

export function getDeployments(): Promise<Deployment[]> {
  return getJson<Deployment[]>("/api/v1/deployments");
}
```

- [ ] **Step 3: Create focused dashboard and failure components**

Create `frontend/src/components/dashboard.tsx`:

```tsx
import type { DashboardResponse, Deployment } from "@/lib/types";

interface DashboardProps {
  dashboard: DashboardResponse;
  deployments: Deployment[];
}

export function Dashboard({ dashboard, deployments }: DashboardProps) {
  return (
    <main className="mx-auto min-h-screen max-w-6xl px-6 py-10">
      <header className="mb-10 flex items-end justify-between gap-6">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-cyan-400">
            Infrastructure learning environment
          </p>
          <h1 className="mt-3 text-4xl font-semibold tracking-tight text-white">
            CloudPulse
          </h1>
        </div>
        <span className="rounded-full border border-emerald-400/30 bg-emerald-400/10 px-4 py-2 text-sm text-emerald-300">
          {dashboard.status}
        </span>
      </header>

      <section aria-label="System metrics" className="grid gap-4 md:grid-cols-3">
        <Metric label="CPU usage" value={`${dashboard.metrics.cpu_percent}%`} />
        <Metric label="Memory usage" value={`${dashboard.metrics.memory_percent}%`} />
        <Metric label="Requests/min" value={String(dashboard.metrics.requests_per_minute)} />
      </section>

      <section className="mt-8 grid gap-6 lg:grid-cols-2">
        <Panel title="Service health">
          <ul className="space-y-3">
            {dashboard.services.map((service) => (
              <li key={service.name} className="flex justify-between border-b border-white/10 pb-3">
                <span className="capitalize text-slate-200">{service.name}</span>
                <span className="text-slate-400">{service.status}</span>
              </li>
            ))}
          </ul>
        </Panel>

        <Panel title="Recent deployments">
          {deployments.length === 0 ? (
            <p className="text-slate-400">No deployments recorded.</p>
          ) : (
            <ul className="space-y-3">
              {deployments.map((deployment) => (
                <li key={deployment.id} className="border-b border-white/10 pb-3">
                  <div className="flex justify-between">
                    <span className="font-medium text-white">{deployment.version}</span>
                    <span className="text-emerald-300">{deployment.status}</span>
                  </div>
                  <p className="mt-1 text-sm text-slate-400">{deployment.environment}</p>
                </li>
              ))}
            </ul>
          )}
        </Panel>
      </section>
    </main>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <article className="rounded-2xl border border-white/10 bg-white/5 p-6">
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-3 text-3xl font-semibold text-white">{value}</p>
    </article>
  );
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="rounded-2xl border border-white/10 bg-white/5 p-6">
      <h2 className="mb-5 text-lg font-semibold text-white">{title}</h2>
      {children}
    </section>
  );
}
```

Create `frontend/src/components/api-unavailable.tsx`:

```tsx
export function ApiUnavailable() {
  return (
    <main className="grid min-h-screen place-items-center px-6">
      <section className="max-w-lg rounded-2xl border border-amber-400/30 bg-amber-400/10 p-8">
        <p className="text-sm font-semibold uppercase tracking-widest text-amber-300">
          API unavailable
        </p>
        <h1 className="mt-3 text-3xl font-semibold text-white">CloudPulse cannot load status data</h1>
        <p className="mt-4 text-slate-300">
          Confirm that FastAPI is running on port 8000, then inspect the backend terminal logs.
        </p>
      </section>
    </main>
  );
}
```

Create `frontend/src/app/loading.tsx`:

```tsx
export default function Loading() {
  return (
    <main className="grid min-h-screen place-items-center px-6">
      <p role="status" className="text-sm uppercase tracking-[0.24em] text-cyan-300">
        Loading infrastructure status…
      </p>
    </main>
  );
}
```

- [ ] **Step 4: Connect the page and global presentation**

Replace `frontend/src/app/page.tsx`:

```tsx
import { ApiUnavailable } from "@/components/api-unavailable";
import { Dashboard } from "@/components/dashboard";
import { getDashboard, getDeployments } from "@/lib/api";

export default async function Home() {
  try {
    const [dashboard, deployments] = await Promise.all([
      getDashboard(),
      getDeployments(),
    ]);
    return <Dashboard dashboard={dashboard} deployments={deployments} />;
  } catch {
    return <ApiUnavailable />;
  }
}
```

Replace `frontend/src/app/layout.tsx`:

```tsx
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CloudPulse",
  description: "Infrastructure-first Cloud and DevOps learning project",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
```

Replace `frontend/src/app/globals.css`:

```css
@import "tailwindcss";

:root {
  color-scheme: dark;
  background: #07111f;
  color: #e2e8f0;
  font-family: Arial, Helvetica, sans-serif;
}

body {
  margin: 0;
  background:
    radial-gradient(circle at top right, rgb(8 145 178 / 18%), transparent 32rem),
    #07111f;
}
```

- [ ] **Step 5: Verify lint and production build**

```bash
cd frontend
npm run lint
npm run build
```

Expected: both commands exit successfully.

- [ ] **Step 6: Commit**

```bash
git add frontend
git commit -m "feat: add CloudPulse infrastructure dashboard"
```

---

### Task 5: Frontend Component Tests

**Files:**
- Create: `frontend/vitest.config.ts`
- Create: `frontend/src/test/setup.ts`
- Create: `frontend/src/components/dashboard.test.tsx`
- Create: `frontend/src/components/api-unavailable.test.tsx`
- Create: `frontend/src/app/loading.test.tsx`
- Modify: `frontend/package.json`

**Interfaces:**
- Consumes: `Dashboard`, `ApiUnavailable`, `DashboardResponse`, and `Deployment` from Task 4.
- Produces: `npm test` as the frontend verification command.

- [ ] **Step 1: Configure Vitest**

Create `frontend/vitest.config.ts`:

```typescript
import path from "node:path";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  resolve: { alias: { "@": path.resolve(__dirname, "./src") } },
  test: {
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
  },
});
```

Create `frontend/src/test/setup.ts`:

```typescript
import "@testing-library/jest-dom/vitest";
```

Add the test script without manually rewriting generated package metadata:

```bash
npm pkg set scripts.test="vitest run"
```

- [ ] **Step 2: Write dashboard and unavailable-state tests**

Create `frontend/src/components/dashboard.test.tsx`:

```tsx
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { Dashboard } from "@/components/dashboard";


describe("Dashboard", () => {
  it("renders metrics, service health, and deployment history", () => {
    render(
      <Dashboard
        dashboard={{
          status: "operational",
          metrics: { cpu_percent: 38.4, memory_percent: 62.1, requests_per_minute: 128 },
          services: [{ name: "api", status: "operational" }],
        }}
        deployments={[
          {
            id: 1,
            version: "v0.1.0",
            environment: "local",
            status: "successful",
            deployed_at: "2026-08-17T12:00:00Z",
          },
        ]}
      />
    );

    expect(screen.getByRole("heading", { name: "CloudPulse" })).toBeInTheDocument();
    expect(screen.getByText("38.4%")).toBeInTheDocument();
    expect(screen.getByText("api")).toBeInTheDocument();
    expect(screen.getByText("v0.1.0")).toBeInTheDocument();
  });

  it("renders an explicit empty deployment state", () => {
    render(
      <Dashboard
        dashboard={{
          status: "operational",
          metrics: { cpu_percent: 0, memory_percent: 0, requests_per_minute: 0 },
          services: [],
        }}
        deployments={[]}
      />
    );

    expect(screen.getByText("No deployments recorded.")).toBeInTheDocument();
  });
});
```

Create `frontend/src/components/api-unavailable.test.tsx`:

```tsx
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ApiUnavailable } from "@/components/api-unavailable";


describe("ApiUnavailable", () => {
  it("tells the operator what to inspect", () => {
    render(<ApiUnavailable />);

    expect(screen.getByText("API unavailable")).toBeInTheDocument();
    expect(screen.getByText(/port 8000/)).toBeInTheDocument();
    expect(screen.getByText(/backend terminal logs/)).toBeInTheDocument();
  });
});
```

Create `frontend/src/app/loading.test.tsx`:

```tsx
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import Loading from "@/app/loading";


describe("Loading", () => {
  it("announces that infrastructure status is loading", () => {
    render(<Loading />);

    expect(screen.getByRole("status")).toHaveTextContent(
      "Loading infrastructure status"
    );
  });
});
```

- [ ] **Step 3: Run the complete frontend verification**

```bash
cd frontend
npm test
npm run lint
npm run build
```

Expected: four component tests pass, lint succeeds, and the production build completes.

- [ ] **Step 4: Commit**

```bash
git add frontend
git commit -m "test: cover dashboard and API failure states"
```

---

### Task 6: Documentation and End-to-End Local Verification

**Files:**
- Create: `docs/architecture.md`
- Create: `docs/troubleshooting.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: documented ports, commands, health endpoints, environment variables, and test commands from Tasks 1–5.
- Produces: a reproducible local startup path and a diagnostic checklist.

- [ ] **Step 1: Document the runtime architecture**

Create `docs/architecture.md`:

````markdown
# CloudPulse Architecture

## Local request path

```text
Browser
  → Next.js on localhost:3000
  → FastAPI on localhost:8000
  → PostgreSQL on localhost:5433
```

Next.js owns presentation. FastAPI owns the API contract, validation, and database access. PostgreSQL stores deployment history only. The separation lets each process later become an independent container and Kubernetes workload.

## Health model

- `GET /health` checks whether the API process can answer HTTP requests.
- `GET /ready` checks whether the API is ready to serve database-backed traffic.
- A process can be alive but not ready; this distinction will later map directly to Kubernetes liveness and readiness probes.

## Data ownership

Mock CPU, memory, and request values come from FastAPI during Milestone 1. PostgreSQL does not store time-series metrics. Prometheus will own that responsibility in the monitoring phase.
````

- [ ] **Step 2: Document diagnostic commands**

Create `docs/troubleshooting.md`:

````markdown
# CloudPulse Troubleshooting

## Check listening ports

```bash
lsof -nP -iTCP:3000 -sTCP:LISTEN
lsof -nP -iTCP:8000 -sTCP:LISTEN
lsof -nP -iTCP:5433 -sTCP:LISTEN
```

An empty result means no process is listening on that port.

## Check the API

```bash
curl -i http://localhost:8000/health
curl -i http://localhost:8000/ready
```

`/health` should return HTTP 200 whenever FastAPI is running. `/ready` returns HTTP 503 when PostgreSQL is unavailable.

## Check PostgreSQL

```bash
/opt/homebrew/opt/postgresql@18/bin/pg_isready -p 5433
brew services list | grep postgresql
```

## Inspect processes

```bash
ps aux | grep -E 'next|uvicorn|postgres' | grep -v grep
```

Read the frontend and backend terminal output before changing configuration.
````

- [ ] **Step 3: Complete the README startup contract**

Replace `README.md` with:

````markdown
# CloudPulse

CloudPulse is an infrastructure-first learning project. The application is a small workload used to learn Linux, networking, Docker, AWS, CI/CD, Kubernetes, Terraform, monitoring, security, and troubleshooting.

## Architecture

```text
Browser → Next.js :3000 → FastAPI :8000 → PostgreSQL :5433
```

The frontend shows a small infrastructure dashboard. FastAPI exposes health, readiness, dashboard, and deployment endpoints. PostgreSQL stores deployment history only.

## Local directories

- `frontend/` — Next.js, TypeScript, and Tailwind CSS
- `backend/` — FastAPI and PostgreSQL access
- `docs/` — architecture and troubleshooting notes

## Local development

### One-time PostgreSQL setup

```bash
brew install postgresql@18
brew services stop postgresql@18
sed -i '' 's/^#port = 5432/port = 5433/' /opt/homebrew/var/postgresql@18/postgresql.conf
brew services start postgresql@18
/opt/homebrew/opt/postgresql@18/bin/createuser -p 5433 --login cloudpulse
/opt/homebrew/opt/postgresql@18/bin/createdb -p 5433 --owner=cloudpulse cloudpulse
/opt/homebrew/opt/postgresql@18/bin/psql -p 5433 -d postgres -c "ALTER ROLE cloudpulse WITH PASSWORD 'cloudpulse';"
```

The committed password is a local demonstration value only and must never be reused for cloud or production infrastructure.

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
cp .env.example .env
alembic upgrade head
python -m scripts.seed
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Open `http://localhost:3000`.

## Tests

```bash
cd backend && source .venv/bin/activate && pytest -q
cd frontend && npm test && npm run lint && npm run build
```

## Operational checks

- API liveness: `curl -i http://localhost:8000/health`
- API readiness: `curl -i http://localhost:8000/ready`
- Interactive API documentation: `http://localhost:8000/docs`
- Troubleshooting guide: `docs/troubleshooting.md`
````

- [ ] **Step 4: Run the final local acceptance check**

Terminal 1:

```bash
brew services start postgresql@18
cd backend
source .venv/bin/activate
alembic upgrade head
python -m scripts.seed
uvicorn app.main:app --reload --port 8000
```

Terminal 2:

```bash
cd frontend
npm run dev
```

Terminal 3:

```bash
curl -fsS http://localhost:8000/health
curl -fsS http://localhost:8000/ready
curl -fsS http://localhost:8000/api/v1/deployments | python3 -m json.tool
curl -I http://localhost:3000
```

Expected: both health endpoints succeed, the deployment record is present, and the frontend returns HTTP 200. Open `http://localhost:3000` and confirm the dashboard shows API data.

- [ ] **Step 5: Verify no secrets or generated directories are tracked**

```bash
git ls-files | grep -E '(^|/)(\.env|node_modules|\.next|\.venv)(/|$)' && exit 1 || true
git diff --check
git status --short
```

Expected: the secret/generated-file search prints nothing, `git diff --check` prints nothing, and status lists only the intended documentation changes.

- [ ] **Step 6: Commit**

```bash
git add README.md docs/architecture.md docs/troubleshooting.md
git commit -m "docs: add local operations and troubleshooting guide"
```

## Final Milestone Gate

Do not begin Docker after the final commit automatically. Review the running system together and confirm the learner can explain:

1. why the frontend calls FastAPI instead of PostgreSQL;
2. the difference between liveness and readiness;
3. what process owns each local port;
4. where secrets belong and why Git ignores them;
5. how to investigate a stopped API or database.

Only after that review should CloudPulse move to the Linux phase.
