from sqlalchemy.orm import Session
from langgraph.types import Command

from app.workflow.graph import graph
from app.core.ids import new_workflow_id


class WorkflowService:
    def __init__(self, db: Session):
        self.db = db

    def start_intake(self, referral: str):
        workflow_id = new_workflow_id()
        state = {"referral": referral, "workflow_id": workflow_id}
        config = {"configurable": {"thread_id": workflow_id}}
        result = graph.invoke(state, config=config)

        return {
            "lead_id": result.get("lead_id"),
            "conversation_id": result.get("conversation_id"),
            "next_question": result.get("next_question"),
            "workflow_id": workflow_id,
            "extracted": result.get("extracted", {}),
            "priority": result.get("priority", {}),
            "missing_fields": result.get("missing_fields", {}),
            "offered_slots": result.get("offered_slots") or [],
            "appointment": result.get("appointment"),
            "booking_message": result.get("booking_message"),
            "completed": result.get("completed", False),
        }

    def continue_workflow(self, workflow_id: str, answer: str):
        config = {"configurable": {"thread_id": workflow_id}}

        print("=============THREAD ID===========")
        print(workflow_id)
        print("==============STATE BEFORE RESUME===============")
        print(graph.get_state(config))

        result = graph.invoke(Command(resume=answer), config=config)
        return result

    def get_state(self, workflow_id: str) -> dict:
        config = {"configurable": {"thread_id": workflow_id}}
        snapshot = graph.get_state(config)
        return snapshot.values or {}

    def update_state(self, workflow_id: str, values: dict) -> None:
        """Patch the checkpointed state for a workflow (e.g. a post-hoc
        correction to an already-collected field) without re-running the
        graph.
        """
        config = {"configurable": {"thread_id": workflow_id}}
        graph.update_state(config, values)
