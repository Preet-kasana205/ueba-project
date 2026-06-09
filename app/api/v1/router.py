from fastapi import APIRouter
from app.api.v1 import ingest, users, baselines

router = APIRouter()
router.include_router(ingest.router, prefix="/ingest", tags=["Ingestion"])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(baselines.router, prefix="/baselines", tags=["Baselines"])