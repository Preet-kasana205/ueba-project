from pydantic import BaseModel, EmailStr
from datetime import datetime


# --- UEBA user management  ---

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


# --- Auth schemas  ---

class AuthRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class AuthLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: str
    username: str
    email: str

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"