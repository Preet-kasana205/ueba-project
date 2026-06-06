from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.event import RawEvent, NormalizedEvent


def parse_timestamp(value: str) -> datetime:
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return datetime.now(timezone.utc)


def normalize_auth_event(payload: dict) -> dict:
    return {
        "event_type": map_auth_action(payload.get("action", "")),
        "event_time": parse_timestamp(payload.get("timestamp", "")),
        "source_ip": payload.get("ip_address"),
        "device_id": payload.get("device_id"),
        "success": payload.get("action", "").endswith("success"),
        "bytes_transferred": None,
        "metadata": {
            "username": payload.get("username"),
            "raw_action": payload.get("action")
        }
    }


def normalize_file_event(payload: dict) -> dict:
    return {
        "event_type": map_file_action(payload.get("operation", "")),
        "event_time": parse_timestamp(payload.get("time", "")),
        "source_ip": None,
        "device_id": payload.get("workstation"),
        "success": True,
        "bytes_transferred": payload.get("bytes"),
        "metadata": {
            "username": payload.get("user"),
            "file_path": payload.get("file_path"),
            "operation": payload.get("operation")
        }
    }


def map_auth_action(action: str) -> str:
    mapping = {
        "login_success": "login_success",
        "login_failed": "login_failed",
        "logout": "logout",
        "password_change": "password_change",
        "privilege_escalation": "privilege_escalation"
    }
    return mapping.get(action, "unknown_auth_event")


def map_file_action(operation: str) -> str:
    mapping = {
        "download": "file_download",
        "upload": "file_upload",
        "delete": "file_delete",
        "view": "file_view",
        "copy": "file_copy"
    }
    return mapping.get(operation, "unknown_file_event")


NORMALIZERS = {
    "auth": normalize_auth_event,
    "file_access": normalize_file_event,
}


def normalize_raw_event(raw_event: RawEvent) -> dict | None:
    normalizer = NORMALIZERS.get(raw_event.source_type)
    if not normalizer:
        return None
    return normalizer(raw_event.payload)


def run_normalization(db: Session) -> dict:
    # Find raw events that have not been normalized yet
    already_normalized = db.query(
        NormalizedEvent.raw_event_id
    ).subquery()

    pending = db.query(RawEvent).filter(
        ~RawEvent.id.in_(already_normalized)
    ).all()

    processed = 0
    failed = 0

    for raw_event in pending:
        try:
            normalized_fields = normalize_raw_event(raw_event)
            if not normalized_fields:
                failed += 1
                continue

            normalized = NormalizedEvent(
                raw_event_id=raw_event.id,
                **normalized_fields
            )
            db.add(normalized)
            processed += 1

        except Exception:
            failed += 1
            continue

    db.commit()

    return {
        "processed": processed,
        "failed": failed
    }