from typing import Annotated

from fastapi import Depends
from sqlalchemy import select

from app.database import SessionDep
from app.models import Deployment
from app.schemas import DeploymentResponse


async def get_recent_deployments(session: SessionDep) -> list[DeploymentResponse]:
    statement = select(Deployment).order_by(Deployment.deployed_at.desc()).limit(10)
    result = await session.scalars(statement)
    return [DeploymentResponse.model_validate(item) for item in result.all()]


RecentDeploymentsDep = Annotated[
    list[DeploymentResponse], Depends(get_recent_deployments)
]
