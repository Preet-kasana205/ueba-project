from fastapi import APIRouter
from app.api.v1 import ingest

router = APIRouter()
router.include_router(ingest.router, prefix="/ingest", tags=["Ingestion"])