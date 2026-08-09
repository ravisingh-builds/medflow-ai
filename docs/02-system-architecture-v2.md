# Architecture

                         ┌───────────────┐
                         │    Patient    │
                         └───────┬───────┘
                                 │
                                 ▼
                    ┌──────────────────────┐
                    │      Frontend        │
                    │  Intake / Chat UI    │
                    └──────────┬───────────┘
                               │ HTTPS
                               ▼
                    ┌──────────────────────┐
                    │      FastAPI         │
                    │      API Layer       │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Application Layer  │
                    │ Conversation Service │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      LangGraph       │
                    │   Workflow Engine    │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
        ┌───────────┐    ┌───────────┐    ┌───────────┐
        │ Extraction│    │  Priority │    │  Planner  │
        │    AI     │    │    AI     │    │    AI     │
        └─────┬─────┘    └─────┬─────┘    └─────┬─────┘
              │                │                │
              └────────────────┼────────────────┘
                               ▼
                         ┌───────────┐
                         │  Gemini   │
                         └───────────┘

                               │
                 ┌─────────────┴─────────────┐
                 ▼                           ▼
        ┌─────────────────┐         ┌─────────────────┐
        │   PostgreSQL    │         │ Future: Memory  │
        │ Leads / Conv.   │         │ Vector Database │
        └─────────────────┘         └─────────────────┘

The important thing here is separation of concerns.

For example:

Frontend doesn't know how LangGraph works.
FastAPI doesn't decide what question to ask.
LangGraph doesn't directly handle HTTP requests.
LLM code doesn't directly manage database transactions.
PostgreSQL doesn't know anything about AI.

That separation becomes very important when we deploy and scale the application.

# important V2 principle

We should not make everything an AI agent. For example:

Extract referral → LLM
Determine priority → LLM
Determine missing fields → deterministic code
Save lead → normal Python/SQL
Create conversation → normal Python/SQL
Authenticate user → normal application logic
Validate phone number → normal validation

AI should be used where reasoning/language is actually useful.


# V2 architecture layers
1. Presentation
React / Next.js / etc.
Responsible for the patient-facing interface.

2. API
FastAPI
Responsible for:

HTTP
authentication
request validation
response formatting

3. Application

ConversationService
LeadService

4. AI / Workflow

LangGraph
   ↓
LLM
   ↓
AI components

Responsible for reasoning and orchestration.

5. Infrastructure

PostgreSQL
Redis (potentially later)
Vector DB (later)
Cloud
Docker

Responsible for persistence and runtime infrastructure.



