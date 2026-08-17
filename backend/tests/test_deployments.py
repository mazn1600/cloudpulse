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
