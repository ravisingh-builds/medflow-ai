from app.core.database import SessionLocal
from app.services.scheduling_service import (
    APPOINTMENT_SLOT_FIELD,
    SchedulingService,
    appointment_to_dict,
)


def confirm_slot_node(state):
    """
    Convert the patient's clicked seat into a SCHEDULED appointment.
    If the hold expired or the seat was taken, clear appointment so the
    graph can re-offer seats.
    """
    slot_id = (state.get("patient_answer") or "").strip()
    workflow_id = state["workflow_id"]
    priority = (state.get("priority") or {}).get("priority", "UNKNOWN")
    extracted = state.get("extracted") or {}

    db = SessionLocal()
    try:
        scheduling = SchedulingService(db)
        appointment = scheduling.confirm_slot(
            workflow_id=workflow_id,
            slot_id=slot_id,
            lead_id=state["lead_id"],
            conversation_id=state.get("conversation_id"),
            priority=priority,
            patient_name=extracted.get("Patient Name") or "",
            diagnosis=extracted.get("Diagnosis") or "",
        )

        if appointment is None:
            # Hold gone — signal the graph to offer again
            state["appointment"] = None
            state["next_question"] = {
                "field": APPOINTMENT_SLOT_FIELD,
                "question": (
                    "That seat is no longer available. Please pick another time."
                ),
            }
            state["offered_slots"] = []
            print("======= confirm_slot: hold miss, will re-offer =====")
            return state

        state["appointment"] = appointment_to_dict(appointment)
        state["offered_slots"] = []
        state["next_question"] = None
        state["booking_message"] = (
            f"You're booked for {state['appointment']['label']}. "
            "We'll see you then!"
        )

        print("======= State RETURNING FROM CONFIRM_SLOT NODE =====")
        print(state["appointment"])

        return state
    finally:
        db.close()
