from app.core.database import SessionLocal

from app.models.lead import Lead
from app.repositories.lead_repository import LeadRepository


def save_lead_node(state):

    db = SessionLocal()

    try:
        repository = LeadRepository(db)

        extracted = state["extracted"]
        priority = state["priority"]

        # This node re-runs on every question/answer loop of the workflow
        # (not just the first time), so once a lead already exists for this
        # thread we update it in place instead of inserting a duplicate.
        if state.get("lead_id"):
            lead = repository.get(state["lead_id"])

            if lead is not None:
                lead.ai_priority = priority.get("priority") or lead.ai_priority
                lead.chief_complaint = extracted.get("Diagnosis") or lead.chief_complaint
                repository.save()
                return state

        patient_name = (extracted.get("Patient Name") or "").strip()

        parts = patient_name.split(maxsplit=1)

        first_name = parts[0] if parts else ""
        last_name = parts[1] if len(parts) > 1 else ""

        lead = Lead(
            first_name=first_name,
            last_name=last_name,
            phone="",
            email="",
            source="Referral",
            chief_complaint=extracted.get("Diagnosis") or "",
            ai_priority=priority.get("priority") or "LOW",
        )

        lead = repository.create(lead)

        state["lead_id"] = str(lead.id)

        print("======= State RETURNING FROM SAVE LEAD NODE =====")
        print(state)


        return state

    finally:
        db.close()