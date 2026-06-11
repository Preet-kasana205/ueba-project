import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.event import RawEvent, NormalizedEvent
from app.models.user import User

logger = logging.getLogger(__name__)


def resolve_user_id(username: str, db: Session) -> str | None:
    if not username:
        return None
    user = db.query(User).filter(
        User.username == username
    ).first()
    return user.id if user else None

def parse_timestamp(value: str) -> datetime:
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise ValueError(f"Invalid ISO-8601 timestamp: {value!r}") from exc

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def normalize_auth_event(payload: dict) -> dict:
    return {
        "event_type": map_auth_action(payload.get("action", "")),
        "event_time": parse_timestamp(payload.get("timestamp", "")),
        "source_ip": payload.get("ip_address"),
        "device_id": payload.get("device_id"),
        "success": payload.get("action", "").endswith("success"),
        "bytes_transferred": None,
        "event_metadata": {
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
        "event_metadata": {
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

            username = normalized_fields["event_metadata"].get("username")
            user_id = resolve_user_id(username, db)

            normalized = NormalizedEvent(
                raw_event_id=raw_event.id,
                user_id=user_id,
                **normalized_fields
            )
            db.add(normalized)
            processed += 1

        except (TypeError, ValueError) as exc:
            logger.warning(
                "Could not normalize raw event %s: %s",
                raw_event.id,
                exc
            )
            failed += 1
            continue

    db.commit()

    return {"processed": processed, "failed": failed}
