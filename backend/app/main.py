from fastapi import FastAPI
from app.api.ai import router as ai_router
from app.models.base import Base
from app.core.database import engine
from app.models.lead import Lead
from app.api.leads import router as lead_router
from app.models.conversation import Conversation
from app.api.conversation import router as conversation_router

app = FastAPI(title="MedFlow AI")

app.include_router(ai_router)
app.include_router(lead_router)
app.include_router(conversation_router)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {
        "message": "Welcome to MedFlow AI"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }

