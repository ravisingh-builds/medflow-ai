"""
version before introducing langgraph

from fastapi import APIRouter

from app.ai.extractor import extract_referral

router = APIRouter(prefix="/ai", tags=["AI"])

@router.post("/extract")
def extract(data: dict):
    result = extract_referral(data["referral"])
    return {
        "result": result
    }
"""

from fastapi import APIRouter

from app.workflow.graph import graph

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/extract")
def extract(data: dict):

    state = {
        "referral": data["referral"],
        "extracted": {},
        "urgency": ""
    }

    result = graph.invoke(state)

    return {
        "result": result["extracted"]
    }