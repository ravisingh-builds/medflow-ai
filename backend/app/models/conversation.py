from uuid import uuid4
from datetime import datetime, timezone

from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Conversation(Base):

    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String,primary_key=True,default=lambda: str(uuid4()),)
    lead_id: Mapped[str] = mapped_column(ForeignKey("leads.id"))
    # LangGraph thread id. Lets a paused conversation be resumed after the
    # process restarts / the browser tab is closed, since it's what
    # `graph.get_state(...)` / `graph.invoke(Command(resume=...))` need.
    workflow_id: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    status: Mapped[str] = mapped_column(default="IN_PROGRESS")
    current_field: Mapped[str]
    current_question: Mapped[str]
    # NEW
    answers: Mapped[str] = mapped_column(default="{}")
    # NEW
    remaining_fields: Mapped[str] = mapped_column(default="[]")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )
