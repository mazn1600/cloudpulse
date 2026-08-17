from fastapi import APIRouter

from app.repositories.deployments import RecentDeploymentsDep
from app.schemas import DeploymentResponse


router = APIRouter(prefix="/api/v1", tags=["deployments"])


@router.get("/deployments")
async def deployments(items: RecentDeploymentsDep) -> list[DeploymentResponse]:
    return items
