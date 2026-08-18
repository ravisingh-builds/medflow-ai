from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.conversation import ConversationReply
from app.services.conversation_service import ConversationService
from app.services.workflow_service import WorkflowService


router = APIRouter(prefix="/conversation",tags=["Conversation"],)

# Pydantic as a tool FastAPI uses to define and validate the shape of incoming data.
"""
HTTP JSON
   │
   ▼
FastAPI
   │
   ▼
Pydantic validation
   │
   ▼
StartConversationRequest
   │
   ├── lead_id
   ├── field
   └── question
"""
class StartConversationRequest(BaseModel):
    lead_id: str
    field: str
    question: str

"""
----------------------------------------------
request: StartConversationRequest

FastAPI gets this from the HTTP request body:

{
  "lead_id": "123",
  "field": "dob",
  "question": "What is your date of birth?"
}

and creates:

StartConversationRequest(...)

---------------------------------------------
db: Depends(get_db)

Depends(get_db) tells FastAPI: "Before running this endpoint, run get_db and use its result as the db argument."

Normal python fucntion:
- def start_conversation(db):
- If you were calling it, you'd have to do:
- db = get_db()
- start_conversation(db)
With FastAPI:
- def start_conversation(db: Session = Depends(get_db)):
- you're telling FastAPI:
When you need to call start_conversation()
             ↓
       call get_db()
             ↓
      take its result
             ↓
       put it into db
             ↓
   call start_conversation(db)

So Depends is basically FastAPI's way of declaring how an argument should be obtained.

Why do we need Depends(get_db)?
- Imagine you have 50 endpoints:
/conversation/start
/conversation/reply
/leads
/leads/{id}
/patients
/patients/{id}
/...
and they all need a database session.
Without dependency injection, you might repeatedly write:
db = get_db()
and manage the lifecycle yourself.
                       
"""

@router.post("/start")
def start_conversation(request: StartConversationRequest, db: Session = Depends(get_db),):

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

    next_question = result.get("next_question")

    return {
        "workflow_id": request.workflow_id,
        "question": next_question["question"] if next_question else None,
        "field": next_question["field"] if next_question else None,
        "completed": next_question is None,
        "extracted": result.get("extracted", {}),
        "priority": (result.get("priority") or {}).get("priority", "UNKNOWN"),
        "missing_fields": (result.get("missing_fields") or {}).get(
            "missing_fields", []
        ),
    }