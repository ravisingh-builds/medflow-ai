# A database schema is the overall structure of the database: tables, columns, data types, constraints, relationships, indexes, etc.

# PostgreSQL
--------------------------------------------------------------
        Docker Network

┌─────────────────────┐        ┌─────────────────────┐
│ FastAPI Container   │        │ PostgreSQL Container│
│                     │        │                     │
│ Python              │        │ Database Engine     │
│ Uvicorn             │───────►│ Stores tables/data  │
│ SQLAlchemy          │        │                     │
└─────────────────────┘        └─────────────────────┘
hostname:                       hostname (inside container) = service name in docker-compose.yml = postgres
---------------------------------------------------------------
PostgreSQL only understands data operations like:
INSERT INTO conversation ...
SELECT * FROM conversation ...
UPDATE lead ...
DELETE ...
-----------------------------------------------------------------

So when someone says: "Save a conversation"

FastAPI cannot magically write into PostgreSQL. It needs something to communicate with the database.

That "something" is what we'll call the Session (db) in the next step.

----------------------------------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------
# Register Lead and Conversation tables

                    DeclarativeBase
                         ↑
                         │
                        Base
                         │
                  Base.metadata
                    /          \
                   /            \
              Lead table    Conversation table
                   \            /
                    \          /
                     create_all()
                          │
                          ▼
                     PostgreSQL

Note: lead and conversation will be registered in the Base.Metadata provided by the /app/model/base.py Class Base(DeclartiveBase) as soon as the main.py executes.
- from app.models.lead import Lead
- from app.models.conversation import Conversation
- Those imports cause Python to execute those model files.
- When Python reaches something like:
- class Lead(Base):
- SQLAlchemy registers the Lead table with Base.metadata.

# create_all() or Base.metadata.create_all(bind=engine)




# db

Your Python application
        │
        ▼
SQLAlchemy Session (`db`)
        │
        ▼
SQLAlchemy / database driver
        │
        ▼
PostgreSQL

# repository

