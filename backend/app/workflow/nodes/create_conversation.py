from app.core.database import SessionLocal

from app.services.conversation_service import ConversationService


def create_conversation_node(state):

    db = SessionLocal()

    try:
        service = ConversationService(db)

        conversation = service.start(
            lead_id=state["lead_id"],
            field=state["next_question"]["field"],
            question=state["next_question"]["question"],
        )

        state["conversation_id"] = str(conversation.id)

        print("======= State RETURNING FROM CREATE_CONVERSATION NODE =====")
        print(state)

        return state

    finally:
        db.close()
