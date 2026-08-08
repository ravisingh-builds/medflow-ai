# MedFlow AI — V1

MedFlow AI is an AI-powered healthcare intake workflow designed to collect and organize patient information from referrals before an appointment is scheduled.

Version 1 focuses on building a reliable, stateful intake workflow using **LangGraph**, an LLM-based question planner, and PostgreSQL-backed persistence.

> **V1 Goal:** Build and understand a working AI workflow that can extract patient information, identify missing information, ask the patient for it, and continue the workflow until the required information has been collected.

---

## Overview

The V1 workflow takes a patient referral as input and processes it through a series of steps:

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