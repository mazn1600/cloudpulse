from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.database import DatabaseStatusDep
from app.schemas import DependencyStatus, HealthResponse, ReadinessResponse


router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="cloudpulse-api")


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    responses={503: {"model": ReadinessResponse}},
)
async def readiness(database: DatabaseStatusDep) -> ReadinessResponse | JSONResponse:
    if database == "down":
        response = ReadinessResponse(
            status="not_ready",
            dependencies=DependencyStatus(database="down"),
        )
        return JSONResponse(status_code=503, content=response.model_dump())

    return ReadinessResponse(
        status="ready",
        dependencies=DependencyStatus(database="up"),
    )
