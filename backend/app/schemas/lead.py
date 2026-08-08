from pydantic import BaseModel


class LeadCreate(BaseModel):
    referral: str


class LeadResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    phone: str
    email: str
    source: str
    chief_complaint: str
    status: str
    ai_priority: str

    model_config = {
        "from_attributes": True
    }