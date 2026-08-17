from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import dashboard, deployments, health
from app.settings import get_settings


settings = get_settings()
app = FastAPI(title="CloudPulse API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)
app.include_router(health.router)
app.include_router(dashboard.router)
app.include_router(deployments.router)
