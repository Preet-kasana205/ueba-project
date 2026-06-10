from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.baseline import run_baseline_computation
import traceback

router = APIRouter()


@router.post("/compute", status_code=200)
def compute_baselines(db: Session = Depends(get_db)):
    try:
        result = run_baseline_computation(db)
        return result
    except Exception as e:
        traceback.print_exc()
        raise