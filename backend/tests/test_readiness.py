from typing import Literal

from fastapi.testclient import TestClient

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
