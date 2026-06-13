import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    fingerprint: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="open",
        index=True
    )
    rule_ids: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    event_ids: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    evidence: Mapped[list[dict]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
