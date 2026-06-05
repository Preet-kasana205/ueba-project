import hashlib
import json
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.event import RawEvent
from app.schemas.event import RawEventIn

def compute_checksum(payload: dict) -> str:
    payload_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload_bytes).hexdigest()

def ingest_batch(
    events: list[RawEventIn],
    db: Session
) -> dict:
    batch_id = str(uuid.uuid4())
    received = 0
    failed = 0

    for event_in in events:
        try:
            checksum = compute_checksum(event_in.payload)

            raw_event = RawEvent(
                source_type=event_in.source_type,
                source_id=event_in.source_id,
                payload=event_in.payload,
                checksum=checksum,
                ingestion_batch=batch_id
            )
            db.add(raw_event)
            received += 1

        except Exception:
            failed += 1
            continue

    db.commit()

    return {
        "batch_id": batch_id,
        "received": received,
        "failed": failed,
        "message": f"Batch ingestion complete. {received} accepted, {failed} failed."
    }