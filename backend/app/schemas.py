from typing import Literal

from pydantic import BaseModel


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
