# MedFlow AI

MedFlow AI is an AI-powered healthcare intake system designed to collect,
organize, and persist patient information from referrals before an appointment
is scheduled.

The system combines LLM-powered reasoning with explicit workflow orchestration
to automate patient intake while maintaining control over application state
and execution.

## V1 — AI-Powered Patient Intake

V1 implements the core patient intake workflow from referral to collection
of the required patient information.

### V1 Capabilities

- Accept a patient referral
- Extract structured patient information from the referral
- Determine referral priority
- Identify missing patient information
- Generate the next appropriate patient question using an LLM
- Pause the workflow while waiting for the patient's response
- Resume the workflow with the patient's answer
- Re-evaluate missing information after each response
- Persist leads in PostgreSQL
- Maintain resumable workflow state using LangGraph checkpointing
- Expose the workflow through a FastAPI backend
- Run the application using Docker

## V1 Workflow

```text
Patient Referral
       │
       ▼
   Extraction
       │
       ▼
    Priority
       │
       ▼
 Missing Fields
       │
       ▼
    Planner
       │
       ▼
 Save Lead
       │
       ▼
Create Conversation
       │
       ▼
   Interrupt
       │
       ▼
 Patient Answer
       │
       ▼
     Reply
       │
       └──────────────┐
                      ▼
               Missing Fields
                      │
                      ▼
                   Planner
                      │
                      ▼
                Next Question