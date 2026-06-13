from sqlalchemy import String, DateTime, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
from app.db.session import Base
import uuid


class RiskScore(Base):
    __tablename__ = "risk_scores"

    id: Mapped[str] = mapped_column(
        String, primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    components: Mapped[dict] = mapped_column(JSONB, nullable=False)
    scored_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )