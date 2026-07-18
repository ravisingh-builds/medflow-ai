from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class Lead:
    id: UUID
    first_name: str
    last_name: str
    phone: str
    email: str
    source: str
    chief_complaint: str

    status: str = "NEW"
    ai_priority: str = "UNKNOWN"

    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

    @classmethod
    def create(
        cls,
        first_name: str,
        last_name: str,
        phone: str,
        email: str,
        source: str,
        chief_complaint: str,
    ):
        return cls(
            id=uuid4(),
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            email=email,
            source=source,
            chief_complaint=chief_complaint,
        )