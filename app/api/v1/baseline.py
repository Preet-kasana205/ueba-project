from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.baseline import run_baseline_computation

router = APIRouter()


@router.post("/compute", status_code=200)
def compute_baselines(db: Session = Depends(get_db)):
    result = run_baseline_computation(db)
    return result