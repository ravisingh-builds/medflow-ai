from app.core.database import SessionLocal
from app.services.conversation_service import ConversationService


def finish_node(state):
    """
    Runs once the planner has no more questions left. Marks the conversation
    row COMPLETED so it drops off the "resume a conversation" list.
    """
    state["completed"] = True

    conversation_id = state.get("conversation_id")

    if conversation_id:
        db = SessionLocal()
        try:
            ConversationService(db).complete(conversation_id)
        finally:
            db.close()

    print("======= State RETURNING FROM FINISH NODE =====")
    print(state)

    return state
