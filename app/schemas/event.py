from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Any

class RawEventIn(BaseModel):
    source_type: str
    source_id: str
    payload: dict[str, Any]

    @field_validator("source_type")
    @classmethod
    def validate_source_type(cls, v):
        allowed = {"auth", "file_access", "network", "endpoint"}
        if v not in allowed:
            raise ValueError(f"source_type must be one of {allowed}")
        return v

class BatchIngestRequest(BaseModel):
    events: list[RawEventIn]
    batch_id: str | None = None

    @field_validator("events")
    @classmethod
    def validate_batch_size(cls, v):
        if len(v) == 0:
            raise ValueError("Batch must contain at least one event")
        if len(v) > 1000:
            raise ValueError("Batch cannot exceed 1000 events")
        return v

class BatchIngestResponse(BaseModel):
    batch_id: str
    received: int
    duplicates: int
    failed: int
    message: str