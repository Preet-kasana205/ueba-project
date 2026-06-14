from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.models.anomaly import Anomaly
from app.models.risk_score import RiskScore

SEVERITY_WEIGHTS = {
    "critical": 35,
    "high":     20,
    "medium":   10,
    "low":       5,
}

ANOMALY_TYPE_WEIGHTS = {
    "data_volume_spike":    1.2,
    "unusual_login_time":   0.8,
    "new_device":           1.0,
    "impossible_travel":    1.5,
    "privilege_escalation": 1.4,
}


def compute_risk_score(user_id: str, db: Session) -> RiskScore:
    since = datetime.now(timezone.utc) - timedelta(hours=24)

    anomalies = db.query(Anomaly).filter(
        Anomaly.user_id == user_id,
        Anomaly.detected_at >= since
    ).all()

    if not anomalies:
        score = 0.0
        components = {}
    else:
        # Take the worst anomaly per type, not sum all
        worst_per_type: dict = {}
        for anomaly in anomalies:
            existing = worst_per_type.get(anomaly.anomaly_type)
            if not existing:
                worst_per_type[anomaly.anomaly_type] = anomaly
            else:
                if anomaly.confidence > existing.confidence:
                    worst_per_type[anomaly.anomaly_type] = anomaly

        components = {}
        raw_score = 0.0

        for anomaly_type, anomaly in worst_per_type.items():
            base = SEVERITY_WEIGHTS.get(anomaly.severity, 5)
            multiplier = ANOMALY_TYPE_WEIGHTS.get(anomaly_type, 1.0)
            contribution = base * multiplier * anomaly.confidence
            components[anomaly_type] = round(contribution, 2)
            raw_score += contribution

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