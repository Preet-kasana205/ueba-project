from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.router import router as api_v1_router

app = FastAPI(
    title="UEBA Platform",
    description="User and Entity Behaviour Analytics for Insider Threat Detection",
    version="0.1.0"
)

app.include_router(api_v1_router, prefix="/api/v1")

@app.get("/health")
def health():
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT
    }