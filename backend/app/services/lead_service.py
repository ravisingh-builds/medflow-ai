from sqlalchemy.orm import Session

from app.models.lead import Lead
from app.repositories.lead_repository import LeadRepository


class LeadService:

    def __init__(self, db: Session):
        self.repository = LeadRepository(db)

    def create(self, lead: Lead):
        return self.repository.create(lead)

    def get(self, lead_id: str):
        return self.repository.get(lead_id)




"""
#The service no longer orchestrates the workflow. It simply starts it.

from sqlalchemy.orm import Session

from app.workflow.graph import graph


class LeadService:

    def __init__(self, db: Session):
        self.db = db

    def create_lead(self, referral: str):

        result = graph.invoke(
            {
                "referral": referral,
                "db": self.db,
            }
        )

        #return result["lead"]
        return {
            "lead": result["lead"],
            "conversation": result["conversation"],
            "next_question": result["next_question"],
        }



from sqlalchemy.orm import Session

from app.ai.extractor import extract_referral
from app.models.lead import Lead
from app.repositories.lead_repository import LeadRepository
from app.ai.priority import classify_priority


class LeadService:

    def __init__(self, db: Session):
        self.repository = LeadRepository(db)

    def create_lead(self, referral: str):

        data = extract_referral(referral)
        priority = classify_priority(referral)

        name = data["Patient Name"].split()

        lead = Lead(
            first_name=name[0],
            last_name=name[-1],
            phone="",
            email="",
            source="Referral",
            chief_complaint=data["Diagnosis"],
            ai_priority=priority["priority"],
        )

        return self.repository.create(lead)

"""