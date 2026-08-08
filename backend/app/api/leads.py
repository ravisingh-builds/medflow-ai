from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.lead import LeadCreate
from app.services.lead_service import LeadService
from app.services.workflow_service import WorkflowService

router = APIRouter(prefix="/leads", tags=["Leads"])

@router.post("")
def create_lead(request: LeadCreate, db: Session = Depends(get_db),):
    
    service = WorkflowService(db)
    
    result = service.start_intake(request.referral)

    return {
        "lead_id": result["lead_id"],
        "conversation_id": result["conversation_id"],
        "question": result["next_question"]["question"],
        "workflow_id": result["workflow_id"],
    }