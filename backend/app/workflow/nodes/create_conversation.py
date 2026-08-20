from app.core.database import SessionLocal
from app.services.conversation_service import ConversationService

def create_conversation_node(state):
    db = SessionLocal()
    try:
        service = ConversationService(db)

        # Idempotent: the first time through, this creates the conversation
        # row; on every later question/answer loop of the same workflow it
        # just updates that same row (see ConversationService.upsert).
        conversation = service.upsert(
            conversation_id=state.get("conversation_id"),
            lead_id=state["lead_id"],
            workflow_id=state.get("workflow_id"),
            field=state["next_question"]["field"],
            question=state["next_question"]["question"],
        )

        state["conversation_id"] = str(conversation.id)

        print("======= State RETURNING FROM CREATE_CONVERSATION NODE =====")
        print(state)

        return state

    finally:
        db.close()
