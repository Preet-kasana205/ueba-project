from sqlalchemy.orm import Session
from app.models.event import NormalizedEvent
from app.models.baseline import Baseline
from app.models.anomaly import Anomaly
from app.detection.rules.login_time import UnusualLoginTimeRule
from app.detection.rules.new_device import NewDeviceRule
from app.detection.rules.data_volume import DataVolumeSpikeRule

RULES = [
    UnusualLoginTimeRule(),
    NewDeviceRule(),
    DataVolumeSpikeRule(),
]


def get_user_baselines(user_id: str, db: Session) -> dict:
    baselines = db.query(Baseline).filter(
        Baseline.user_id == user_id,
        Baseline.is_current == True
    ).all()
    return {b.baseline_type: b for b in baselines}


def run_detection(db: Session) -> dict:
    # Find normalized events not yet checked
    already_checked_subq = db.query(
        Anomaly.normalized_event_id,
        Anomaly.anomaly_type
    ).subquery()

    pending = db.query(NormalizedEvent).filter(
        NormalizedEvent.user_id.isnot(None)
    ).all()

    anomalies_found = 0

    for event in pending:
        baselines = get_user_baselines(event.user_id, db)

        for rule in RULES:
            result = rule.evaluate(event, baselines)

            if not result.fired:
                continue

            # Check if this exact event + rule combo already exists
            exists = db.query(Anomaly).filter(
                Anomaly.normalized_event_id == event.id,
                Anomaly.anomaly_type == result.anomaly_type
            ).first()

            if exists:
                continue

            anomaly = Anomaly(
                normalized_event_id=event.id,
                user_id=event.user_id,
                anomaly_type=result.anomaly_type,
                severity=result.severity,
                confidence=result.confidence,
                explanation=result.explanation
            )
            db.add(anomaly)
            anomalies_found += 1

    db.commit()
    return {"anomalies_found": anomalies_found}