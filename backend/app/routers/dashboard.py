from fastapi import APIRouter

from app.schemas import DashboardResponse, MetricSnapshot, ServiceSnapshot


router = APIRouter(prefix="/api/v1", tags=["dashboard"])


@router.get("/dashboard")
def dashboard() -> DashboardResponse:
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
