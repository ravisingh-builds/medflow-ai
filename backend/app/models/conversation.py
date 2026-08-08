from uuid import uuid4

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    lead_id: Mapped[str] = mapped_column(
        ForeignKey("leads.id")
    )

    status: Mapped[str] = mapped_column(
        default="IN_PROGRESS"
    )

    current_field: Mapped[str]

    current_question: Mapped[str]

    # NEW
    answers: Mapped[str] = mapped_column(
        default="{}"
    )

    # NEW
    remaining_fields: Mapped[str] = mapped_column(
        default="[]"
    )