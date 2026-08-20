from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4())
    )
    lead_id: Mapped[str] = mapped_column(ForeignKey("leads.id"), index=True)
    conversation_id: Mapped[str | None] = mapped_column(
        ForeignKey("conversations.id"), nullable=True
    )
    workflow_id: Mapped[str] = mapped_column(String, index=True)

    slot_id: Mapped[str] = mapped_column(String, index=True)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    doctor_name: Mapped[str] = mapped_column(String)
    priority: Mapped[str] = mapped_column(String, default="UNKNOWN")

    # SCHEDULED | COMPLETED | CANCELLED
    status: Mapped[str] = mapped_column(String, default="SCHEDULED", index=True)
    calendar_event_id: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )
