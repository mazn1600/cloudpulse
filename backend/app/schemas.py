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
