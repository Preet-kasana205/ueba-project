from pydantic import BaseModel
from datetime import datetime


class UserCreate(BaseModel):
    external_id: str
    username: str
    department: str | None = None
    role: str | None = None


class UserResponse(BaseModel):
    id: str
    external_id: str
    username: str
    department: str | None
    role: str | None
    risk_level: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}