from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.ai.correction import parse_correction
from app.core.dependencies import get_db
from app.api.workflow_response import workflow_response
from app.schemas.conversation import ConversationReply
from app.services.conversation_service import ConversationService
from app.services.lead_service import LeadService
from app.services.scheduling_service import SchedulingService
from app.services.workflow_service import WorkflowService


router = APIRouter(prefix="/conversation", tags=["Conversation"])


class CorrectionRequest(BaseModel):
    text: str


class StartConversationRequest(BaseModel):
    lead_id: str
    field: str
    question: str


@router.post("/start")
def start_conversation(
    request: StartConversationRequest,
    db: Session = Depends(get_db),
):
    service = ConversationService(db)
    conversation = service.start(
        lead_id=request.lead_id,
        field=request.field,
        question=request.question,
    )
    return conversation


@router.post("/reply")
def reply(request: ConversationReply, db: Session = Depends(get_db)):
    workflow = WorkflowService(db)
    result = workflow.continue_workflow(
        workflow_id=request.workflow_id,
        answer=request.answer,
    )
    return workflow_response(request.workflow_id, result)


@router.get("/resumable")
def list_resumable(db: Session = Depends(get_db)):
    service = ConversationService(db)
    return service.list_resumable()


@router.get("/{workflow_id}/resume")
def resume(workflow_id: str, db: Session = Depends(get_db)):
    workflow = WorkflowService(db)
    values = workflow.get_state(workflow_id)

    if not values:
        raise HTTPException(status_code=404, detail="Workflow not found")

    lead_id = values.get("lead_id")
    lead = LeadService(db).get(lead_id) if lead_id else None

    # Prefer live DB appointment (status may have changed via staff complete)
    appointment = values.get("appointment")
    live = SchedulingService(db).get_by_workflow(workflow_id)
    if live is not None:
        appointment = live
        values = {**values, "appointment": live}

    payload = workflow_response(workflow_id, values)
    payload.update(
        {
            "conversation_id": values.get("conversation_id"),
            "lead_id": lead_id,
            "patient_name": f"{lead.first_name} {lead.last_name}".strip()
            if lead
            else None,
            "chief_complaint": lead.chief_complaint if lead else None,
            "appointment": appointment,
        }
    )
    return payload


@router.post("/{workflow_id}/correct")
def correct(
    workflow_id: str,
    request: CorrectionRequest,
    db: Session = Depends(get_db),
):
    """Apply a free-text correction (e.g. "please correct my DOB to
    1990-01-01") to a workflow's already-collected fields, after the intake
    itself has finished — used when a patient reviews a booked appointment
    and asks for a fix.
    """
    workflow = WorkflowService(db)
    values = workflow.get_state(workflow_id)

    if not values:
        raise HTTPException(status_code=404, detail="Workflow not found")

    field, new_value = parse_correction(request.text)

    if not field or not new_value:
        return {
            "workflow_id": workflow_id,
            "field": None,
            "applied": False,
            "message": (
                'I couldn\'t tell what to update from that. Try something '
                'like "please correct my date of birth to 1990-01-01".'
            ),
            "extracted": values.get("extracted", {}),
        }

    extracted = dict(values.get("extracted") or {})
    old_value = extracted.get(field)
    extracted[field] = new_value
    workflow.update_state(workflow_id, {"extracted": extracted})

    lead_id = values.get("lead_id")
    if lead_id:
        lead_service = LeadService(db)
        lead = lead_service.get(lead_id)

        if lead is not None:
            if field == "Patient Name":
                parts = new_value.split(maxsplit=1)
                lead.first_name = parts[0] if parts else lead.first_name
                lead.last_name = parts[1] if len(parts) > 1 else ""
                lead_service.repository.save()
            elif field == "Diagnosis":
                lead.chief_complaint = new_value
                lead_service.repository.save()

    return {
        "workflow_id": workflow_id,
        "field": field,
        "old_value": old_value,
        "applied": True,
        "message": f'Updated {field} to "{new_value}".',
        "extracted": extracted,
    }
