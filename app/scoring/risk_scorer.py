from sqlalchemy.orm import Session
from app.models.anomaly import Anomaly
from app.models.risk_score import RiskScore

SEVERITY_WEIGHTS = {
    "critical": 40,
    "high":     25,
    "medium":   15,
    "low":       5,
}

ANOMALY_TYPE_WEIGHTS = {
    "data_volume_spike":   1.3,
    "unusual_login_time":  1.0,
    "new_device":          1.2,
    "impossible_travel":   1.5,
    "privilege_escalation": 1.4,
}


def compute_risk_score(user_id: str, db: Session) -> RiskScore:
    # Get unscored anomalies for this user
    anomalies = db.query(Anomaly).filter(
        Anomaly.user_id == user_id
    ).order_by(Anomaly.detected_at.desc()).limit(20).all()

    if not anomalies:
        score = 0.0
        components = {}
    else:
        components = {}
        raw_score = 0.0

        for anomaly in anomalies:
            base = SEVERITY_WEIGHTS.get(anomaly.severity, 5)
            multiplier = ANOMALY_TYPE_WEIGHTS.get(anomaly.anomaly_type, 1.0)
            contribution = base * multiplier * anomaly.confidence
            components[anomaly.anomaly_type] = round(contribution, 2)
            raw_score += contribution

        # Cap at 100
        score = min(round(raw_score, 2), 100.0)

    risk_score = RiskScore(
        user_id=user_id,
        score=score,
        components=components
    )
    db.add(risk_score)
    db.commit()
    db.refresh(risk_score)
    return risk_score