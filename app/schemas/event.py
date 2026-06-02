from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Any

class RawEventIn(BaseModel):
    source_type: str
    source_id: str
    timestamp: datetime
    payload: dict[str, Any]

    @field_validator("source_type")
    @classmethod
    def validate_source_type(cls, v):
        allowed = {"auth", "file_access", "network", "endpoint"}
        if v not in allowed:
            raise ValueError(f"source_type must be one of {allowed}")
        return v

    @field_validator("payload")
    @classmethod
    def validate_payload_not_empty(cls, v):
        if not v:
            raise ValueError("payload cannot be empty")
        return v


class BatchIngestRequest(BaseModel):
    events: list[RawEventIn]

    @field_validator("events")
    @classmethod
    def validate_batch_size(cls, v):
        if len(v) == 0:
            raise ValueError("batch must contain at least one event")
        if len(v) > 1000:
            raise ValueError("batch cannot exceed 1000 events")
        return v


class BatchIngestResponse(BaseModel):
    batch_id: str
    received: int
    duplicates_skipped: int
    stored: int