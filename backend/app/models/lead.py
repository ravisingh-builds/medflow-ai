from uuid import uuid4
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class Lead(Base):
    
    __tablename__ = "leads"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()),)

    first_name: Mapped[str]
    last_name: Mapped[str]
    phone: Mapped[str]
    email: Mapped[str]
    source: Mapped[str]
    chief_complaint: Mapped[str]

    status: Mapped[str] = mapped_column(default="NEW")

    ai_priority: Mapped[str] = mapped_column(default="UNKNOWN")