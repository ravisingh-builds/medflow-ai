from sqlalchemy.orm import Session

from app.models.lead import Lead


class LeadRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, lead: Lead):

        self.db.add(lead)
        self.db.commit()
        self.db.refresh(lead)

        return lead

    def get(self, lead_id: str):
        return self.db.get(Lead, lead_id)

    def save(self):
        self.db.commit()