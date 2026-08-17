from fastapi import APIRouter

from app.schemas import HealthResponse


router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="cloudpulse-api")
