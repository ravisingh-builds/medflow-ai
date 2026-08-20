from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SlotHold(Base):
    """
    Soft seat-hold while a patient is choosing among offered slots.
    Expired / released holds free the seat for others.
    """

    __tablename__ = "slot_holds"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4())
    )
    slot_id: Mapped[str] = mapped_column(String, index=True)
    workflow_id: Mapped[str] = mapped_column(String, index=True)

    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    doctor_name: Mapped[str] = mapped_column(String)

    # ACTIVE | RELEASED | CONVERTED
    status: Mapped[str] = mapped_column(String, default="ACTIVE", index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
