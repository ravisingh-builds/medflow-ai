from app.workflow.state import ReferralState
from app.services.scheduling_service import APPOINTMENT_SLOT_FIELD


def should_continue(state: ReferralState):
    """Route to more intake questions, or into appointment scheduling."""
    if state.get("next_question") is None:
        return "schedule"
    return "wait"


def after_interrupt(state: ReferralState):
    """Intake answers go to reply; seat picks go to confirm."""
    next_question = state.get("next_question") or {}
    if next_question.get("field") == APPOINTMENT_SLOT_FIELD:
        return "confirm"
    return "reply"


def after_confirm(state: ReferralState):
    if state.get("appointment"):
        return "finish"
    return "reoffer"
