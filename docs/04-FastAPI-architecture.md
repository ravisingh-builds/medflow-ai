# main.py; app = FastAPI(title = "MedFlow AI")

FastAPI class
     │
     │ instantiate
     ▼
┌─────────────────────┐
│ app                 │
│                     │
│ routes              │
│ middleware          │
│ configuration       │
│ exception handlers  │
│ OpenAPI information │
│ ...                 │
└─────────────────────┘

# main.py; app.include_router(conversation_router)

conceptually:

1. app/api/conversation.py

    router = APIRouter(...)

    @router.post("/start")
    def start_conversation(...):
    
2. main.py

app.include_router(conversation_router)

3. results in the FastAPI application knowing:

POST /conversation/start  (not api endpoint)
        ↓
start_conversation()       (note python functon)

4. What do you think happens between that HTTP request arriving at Uvicorn and your start_conversation() function being executed?

Browser / Frontend
        │
        │ HTTP POST /conversation/start
        ▼
     Uvicorn
        │
        ▼
   FastAPI `app`
        │
        │ route matching
        ▼
conversation route
        │
        ▼
start_conversation()

5. 
docker compose up --build
        │
        ├── Build Docker image
        │
        └── Start container
                 │
                 ▼
             Docker runs
             CMD
                 │
                 ▼
             Uvicorn
                 │
                 ▼
          imports app.main
                 │
                 ▼
       creates FastAPI `app`
                 │
                 ▼
       startup event executes
                 │
                 ▼
       Base.metadata.create_all(...)
                 │
                 ▼
       Uvicorn starts accepting requests


6. Concern:

Imagine production has:
            Load Balancer
             /     |     \
            ▼      ▼      ▼
          API-1  API-2  API-3
            \      |      /
             \     |     /
              ▼    ▼    ▼
               PostgreSQL
Every API container starts its own Uvicorn process.
If every application startup executes:
Base.metadata.create_all(bind=engine)
then all three application instances are involved in database schema management.
We're not saying create_all() is "wrong Python."
We're saying:
Database schema management and application process startup are different responsibilities.
