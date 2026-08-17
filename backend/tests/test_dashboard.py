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
