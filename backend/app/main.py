from fastapi import FastAPI

from app.models.base import Base

from app.models.lead import Lead
# as soon as it executes -
# Python imports Lead
# class Lead(Base) executes
# SQLAlchemy builds the table definition
# Base.metadata now knows about "leads"
# Lead table is not created yet or PostgreSQL hasn't been asked to create the table yet.
# Think of it as creating a blueprint in Python memory, not building the actual building.
from app.models.conversation import Conversation
from app.models.appointment import Appointment  # noqa: F401
from app.models.slot_hold import SlotHold  # noqa: F401

from app.core.database import engine

from app.api.ai import router as ai_router
from app.api.leads import router as lead_router
from app.api.conversation import router as conversation_router
from app.api.appointments import router as appointments_router

from fastapi.middleware.cors import CORSMiddleware


# create a FastAPI application object in memory
# note it's not a simple python object because it will hold the configuration and routing information for your web application.

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# registering the routes contained in that router with the FastAPI application.
app.include_router(ai_router)
app.include_router(lead_router)
app.include_router(conversation_router)
app.include_router(appointments_router)

# "Take all these table definitions (as imported above in import Lead and import conversation) and check the actual database. If a table doesn't exist, create it."
# SQLAlchemy communicates with PostgreSQL
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

