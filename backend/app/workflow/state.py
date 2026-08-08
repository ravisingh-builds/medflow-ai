from typing import TypedDict


class ReferralState(TypedDict, total=False):
    # Initial input
    referral: str

    # AI outputs
    extracted: dict
    priority: dict
    missing_fields: dict

    # Conversation
    next_question: dict
    patient_answer: str

    # Persisted entity IDs
    lead_id: str
    conversation_id: str