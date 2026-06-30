from sqlalchemy.orm import Session
from app.models.anomaly import Anomaly
from app.models.alert import Alert
from app.models.user import User
from app.scoring.risk_scorer import compute_risk_score

VERIFICATION_THRESHOLD = 70.0

SEVERITY_PRIORITY = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1
}


def get_alert_severity(anomalies: list) -> str:
    if not anomalies:
        return "low"
    highest = max(
        anomalies,
        key=lambda a: SEVERITY_PRIORITY.get(a.severity, 0)
    )
    return highest.severity


def build_alert_title(anomalies: list, username: str) -> str:
    types = list(set(a.anomaly_type for a in anomalies))
    if len(types) == 1:
        readable = types[0].replace("_", " ").title()
        return f"{readable} detected for {username}"
    return f"Multiple anomalies detected for {username} ({len(types)} types)"


def build_alert_description(anomalies: list) -> str:
    lines = []
    for a in anomalies:
        interpretation = a.explanation.get(
            "interpretation", a.anomaly_type
        )
        lines.append(f"• {interpretation}")
    return "\n".join(lines)




def run_alert_engine(db: Session) -> dict:
    # Get all anomaly IDs already included in existing alerts
    existing_alerts = db.query(Alert).all()
    alerted_anomaly_ids = set()
    for alert in existing_alerts:
        for aid in alert.anomaly_ids:
            alerted_anomaly_ids.add(aid)

    # Get all anomalies
    all_anomalies = db.query(Anomaly).all()

    # Filter out already alerted ones in Python
    unalerted_anomalies = [
        a for a in all_anomalies
        if a.id not in alerted_anomaly_ids
    ]

    if not unalerted_anomalies:
        return {"alerts_created": 0}

    # Group by user
    by_user: dict = {}
    for anomaly in unalerted_anomalies:
        by_user.setdefault(anomaly.user_id, []).append(anomaly)

    alerts_created = 0

    for user_id, anomalies in by_user.items():
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            continue

        risk_score = compute_risk_score(user_id, db)

        alert = Alert(
            user_id=user_id,
            title=build_alert_title(anomalies, user.username),
            description=build_alert_description(anomalies),
            risk_score=risk_score.score,
            severity=get_alert_severity(anomalies),
            status="open",
            requires_verification=risk_score.score >= VERIFICATION_THRESHOLD,
            anomaly_ids=[a.id for a in anomalies]
        )
        db.add(alert)

        if risk_score.score >= 80:
            user.risk_level = "critical"
        elif risk_score.score >= 60:
            user.risk_level = "high"
        elif risk_score.score >= 40:
            user.risk_level = "medium"
        else:
            user.risk_level = "low"

        alerts_created += 1

    db.commit()
    return {"alerts_created": alerts_created}

    