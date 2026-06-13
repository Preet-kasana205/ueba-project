from fastapi import APIRouter
from app.api.v1 import ingest, users, baseline, detection

router = APIRouter()
router.include_router(ingest.router, prefix="/ingest", tags=["Ingestion"])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(baseline.router, prefix="/baseline", tags=["Baseline"])
router.include_router(detection.router, prefix="/detection", tags=["Detection"])
