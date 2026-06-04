from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(
    title="UEBA Platform",
    description="User and Entity Behaviour Analytics for Insider Threat Detection",
    version="0.1.0"
)

@app.get("/health")
def health():
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT
    }