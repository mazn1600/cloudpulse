from typing import Literal

import pytest
from fastapi.testclient import TestClient

import app.database as database_module
from app.database import get_database_status
from app.main import app


client = TestClient(app)


async def database_up() -> Literal["up"]:
    return "up"


async def database_down() -> Literal["down"]:
    return "down"


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


class RefusedEngine:
    def connect(self) -> "RefusedEngine":
        return self

    async def __aenter__(self) -> None:
        raise ConnectionRefusedError("connection refused")

    async def __aexit__(self, *args: object) -> None:
        return None


async def test_database_status_is_down_when_connection_is_refused(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(database_module, "engine", RefusedEngine())

    assert await get_database_status() == "down"
