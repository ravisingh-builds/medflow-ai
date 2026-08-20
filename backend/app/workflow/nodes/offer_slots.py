from app.core.database import SessionLocal
from app.services.conversation_service import ConversationService
from app.services.scheduling_service import (
    APPOINTMENT_SLOT_FIELD,
    SchedulingService,
)


def offer_slots_node(state):
    """
    After intake is complete: soft-hold priority-filtered seats and ask the
    patient to pick one (movie-seat style).
    """
    workflow_id = state["workflow_id"]
    priority = (state.get("priority") or {}).get("priority", "UNKNOWN")

    db = SessionLocal()
    try:
        # Ensure lead exists even when every field was filled on the first pass
        # (that path never hit save_lead before).
        from app.workflow.nodes.save_lead import save_lead_node

        state = save_lead_node(state)

        scheduling = SchedulingService(db)
        offered = scheduling.offer_slots(
            workflow_id=workflow_id,
            priority=priority,
        )

        question = (
            "Intake is complete — please choose an appointment time. "
            "These seats are held for you for a few minutes."
        )
        if not offered:
            question = (
                "Intake is complete, but no appointment seats are free right "
                "now. Please try again shortly."
            )

        state["offered_slots"] = offered
        state["next_question"] = {
            "field": APPOINTMENT_SLOT_FIELD,
            "question": question,
        }
        state["appointment"] = None

        conversation = ConversationService(db).upsert(
            conversation_id=state.get("conversation_id"),
            lead_id=state["lead_id"],
            workflow_id=workflow_id,
            field=APPOINTMENT_SLOT_FIELD,
            question=question,
        )
        state["conversation_id"] = str(conversation.id)

        print("======= State RETURNING FROM OFFER_SLOTS NODE =====")
        print({"offered_slots": offered, "priority": priority})

        return state
    finally:
        db.close()
