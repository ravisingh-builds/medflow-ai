# MedFlow AI — V1 System Architecture

## 1. Purpose

This document describes the architecture of MedFlow AI V1.

V1 is an AI-powered healthcare intake workflow that processes a patient
referral, extracts relevant information, identifies missing information,
interacts with the patient to collect the missing information, and persists
the resulting lead.

The workflow is implemented using LangGraph.

---

## 2. High-Level Architecture

                    ┌────────────────────┐
                    │       Client       │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │      FastAPI       │
                    │       API          │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │     LangGraph      │
                    │      Workflow      │
                    └─────────┬──────────┘
                              │
             ┌────────────────┼────────────────┐
             │                │                │
             ▼                ▼                ▼
       ┌───────────┐   ┌───────────┐   ┌────────────┐
       │ Extraction│   │  Priority │   │  Planner   │
       │    LLM    │   │    LLM    │   │    LLM     │
       └───────────┘   └───────────┘   └────────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │    PostgreSQL      │
                    │ Persistent Storage │
                    └────────────────────┘

                    ┌────────────────────┐
                    │ LangGraph          │
                    │ Checkpointer       │
                    └────────────────────┘