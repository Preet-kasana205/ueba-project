from fastapi import FastAPI
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from app.core.config import settings
from app.api.v1.router import router as api_v1_router
from app.db.session import SessionLocal
from app.services.normalization import run_normalization


def run_scheduled_normalization():
    db = SessionLocal()
    try:
        run_normalization(db)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        run_scheduled_normalization,
        trigger="interval",
        seconds=60,
        id="normalization_job"
    )
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(
    title="UEBA Platform",
    description="User and Entity Behaviour Analytics for Insider Threat Detection",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT
    }