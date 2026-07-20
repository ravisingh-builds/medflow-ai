from fastapi import APIRouter

from app.ai.extractor import extract_referral

router = APIRouter(prefix="/ai", tags=["AI"])

@router.post("/extract")
def extract(data: dict):
    result = extract_referral(data["referral"])
    return {
        "result": result
    }