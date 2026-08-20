from app.services.scheduling_service import APPOINTMENT_SLOT_FIELD


def workflow_response(workflow_id: str, result: dict) -> dict:
    """Shared shape for /leads, /conversation/reply, and resume."""
    next_question = result.get("next_question")
    field = next_question["field"] if next_question else None
    awaiting_slots = field == APPOINTMENT_SLOT_FIELD
    appointment = result.get("appointment")
    completed = bool(appointment) or (
        next_question is None and not awaiting_slots and result.get("completed", False)
    )

    # When graph is mid-scheduling with no seats, still treat as awaiting UI
    if awaiting_slots:
        completed = False

    return {
        "workflow_id": workflow_id,
        "question": next_question["question"] if next_question else None,
        "field": field,
        "completed": completed,
        "awaiting_slots": awaiting_slots,
        "offered_slots": result.get("offered_slots") or [],
        "appointment": appointment,
        "booking_message": result.get("booking_message"),
        "extracted": result.get("extracted", {}),
        "priority": (result.get("priority") or {}).get("priority", "UNKNOWN"),
        "missing_fields": (result.get("missing_fields") or {}).get(
            "missing_fields", []
        ),
    }
