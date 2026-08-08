from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.conversation import ConversationReply
from app.services.conversation_service import ConversationService
from app.services.workflow_service import WorkflowService


router = APIRouter(
    prefix="/conversation",
    tags=["Conversation"],
)


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
def reply(request: ConversationReply, db: Session = Depends(get_db),):
    
    workflow = WorkflowService(db)

    result = workflow.continue_workflow(workflow_id=request.workflow_id, answer=request.answer,)

    return {
        "workflow_id": request.workflow_id,
        "question": (
            result["next_question"]["question"]
            if result["next_question"]
            else None
        ),
        "completed": result["next_question"] is None,
    }