from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
from app.db.session import Base
import uuid


class UserDevice(Base):
    __tablename__ = "user_devices"

    id: Mapped[str] = mapped_column(
        String, primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    device_id: Mapped[str] = mapped_column(String(255), nullable=False)
    first_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    is_trusted: Mapped[bool] = mapped_column(Boolean, default=False)