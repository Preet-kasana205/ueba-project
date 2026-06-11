from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.models.event import NormalizedEvent
from app.models.baseline import Baseline
from app.models.user import User
from app.models.device import UserDevice

BASELINE_WINDOW_DAYS = 30
TRAINING_LAG_HOURS = 24


def compute_login_hour_baseline(
    user_id: str,
    events: list,
    db: Session
) -> dict:
    login_events = [
        e for e in events
        if e.event_type in ("login_success", "login_failed")
    ]

    if not login_events:
        return {}

    hours = [e.event_time.hour for e in login_events]
    mean_hour = sum(hours) / len(hours)
    variance = sum((h - mean_hour) ** 2 for h in hours) / len(hours)
    std_dev = variance ** 0.5

    return {
        "mean_hour": round(mean_hour, 2),
        "std_dev": round(std_dev, 2),
        "min_hour": min(hours),
        "max_hour": max(hours),
        "sample_hours": hours
    }


def compute_device_baseline(
    user_id: str,
    events: list,
    db: Session
) -> dict:
    devices = set(
        e.device_id for e in events
        if e.device_id is not None
    )

    # Update user device registry
    for device_id in devices:
        existing = db.query(UserDevice).filter(
            UserDevice.user_id == user_id,
            UserDevice.device_id == device_id
        ).first()

        if not existing:
            db.add(UserDevice(
                user_id=user_id,
                device_id=device_id
            ))
        else:
            existing.last_seen = datetime.now(timezone.utc)

    return {
        "known_devices": sorted(devices),
        "device_count": len(devices)
    }


def compute_data_volume_baseline(
    user_id: str,
    events: list,
    db: Session
) -> dict:
    transfer_events = [
        e for e in events
        if e.bytes_transferred is not None
        and e.bytes_transferred > 0
    ]

    if not transfer_events:
        return {"mean_daily_bytes": 0, "std_dev": 0, "max_daily_bytes": 0}

    # Group by day
    daily_volumes: dict = {}
    for e in transfer_events:
        day = e.event_time.date().isoformat()
        daily_volumes[day] = daily_volumes.get(day, 0) + e.bytes_transferred

    volumes = list(daily_volumes.values())
    mean = sum(volumes) / len(volumes)
    variance = sum((v - mean) ** 2 for v in volumes) / len(volumes)
    std_dev = variance ** 0.5

    return {
        "mean_daily_bytes": round(mean, 2),
        "std_dev": round(std_dev, 2),
        "max_daily_bytes": max(volumes)
    }


BASELINE_COMPUTERS = {
    "login_hours": compute_login_hour_baseline,
    "known_devices": compute_device_baseline,
    "data_volume": compute_data_volume_baseline,
}


def compute_baselines_for_user(user_id: str, db: Session) -> dict:
    window_end = datetime.now(timezone.utc) - timedelta(
        hours=TRAINING_LAG_HOURS
    )
    window_start = window_end - timedelta(days=BASELINE_WINDOW_DAYS)

    events = db.query(NormalizedEvent).filter(
        NormalizedEvent.user_id == user_id,
        NormalizedEvent.event_time >= window_start,
        NormalizedEvent.event_time < window_end
    ).all()

    if not events:
        return {"user_id": user_id, "baselines_computed": 0}

    computed = 0

    for baseline_type, computer in BASELINE_COMPUTERS.items():
        parameters = computer(user_id, events, db)

        if not parameters:
            continue

        # Mark previous baselines as not current
        db.query(Baseline).filter(
            Baseline.user_id == user_id,
            Baseline.baseline_type == baseline_type,
            Baseline.is_current == True
        ).update({"is_current": False})

        baseline = Baseline(
            user_id=user_id,
            baseline_type=baseline_type,
            parameters=parameters,
            event_count=len(events),
            window_days=BASELINE_WINDOW_DAYS
        )
        db.add(baseline)
        computed += 1

    db.commit()
    return {"user_id": user_id, "baselines_computed": computed}


def run_baseline_computation(db: Session) -> dict:
    users = db.query(User).filter(User.is_active == True).all()
    total = 0

    for user in users:
        result = compute_baselines_for_user(user.id, db)
        total += result["baselines_computed"]

    return {"total_baselines_computed": total}
