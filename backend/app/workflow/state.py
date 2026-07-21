from typing import TypedDict


class ReferralState(TypedDict):
    referral: str
    extracted: dict
    urgency: str