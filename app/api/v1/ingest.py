from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.event import BatchIngestRequest, BatchIngestResponse
from app.services.ingestion import ingest_batch

router = APIRouter()

@router.post("/events/batch", response_model=BatchIngestResponse, status_code=202)
def ingest_events(
    request: BatchIngestRequest,
    db: Session = Depends(get_db)
):
    result = ingest_batch(request.events, db)
    return result