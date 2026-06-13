from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.alert import Alert
from app.services.alert_engine import run_alert_engine

router = APIRouter()


@router.post("/generate", status_code=200)
def generate_alerts(db: Session = Depends(get_db)):
    result = run_alert_engine(db)
    return result


@router.get("/")
def list_alerts(db: Session = Depends(get_db)):
    alerts = db.query(Alert).order_by(
        Alert.created_at.desc()
    ).all()
    return [
        {
            "id": a.id,
            "user_id": a.user_id,
            "title": a.title,
            "description": a.description,
            "risk_score": a.risk_score,
            "severity": a.severity,
            "status": a.status,
            "requires_verification": a.requires_verification,
            "created_at": a.created_at
        }
        for a in alerts
    ]


@router.patch("/{alert_id}/status")
def update_alert_status(
    alert_id: str,
    status: str,
    db: Session = Depends(get_db)
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    allowed = {"open", "acknowledged", "escalated", "closed"}
    if status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Status must be one of {allowed}"
        )

    alert.status = status
    db.commit()
    return {"message": f"Alert status updated to {status}"}