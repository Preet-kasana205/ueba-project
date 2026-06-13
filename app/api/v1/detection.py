from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.detection import run_detection

router = APIRouter()


@router.post("/run", status_code=200)
def trigger_detection(db: Session = Depends(get_db)):
    result = run_detection(db)
    return result