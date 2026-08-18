# Docker container

Docker container
      │
      ▼
Uvicorn (listening on port 8000)
      │
      │ HTTP request
      ▼
FastAPI `app` object
      │
      ▼
matching route
      │
      ▼
your Python endpoint function

# Uvicorn 

It is an ASGI web server. Its job is to listen for network requests and hand those requests to your FastAPI application.
Uvicorn is the network-facing server process that accepts HTTP requests and invokes your FastAPI application to handle them.

uvicorn app.main:app
             │    │
             │    └── the `app` object
             │        inside main.py
             │
             └────── the Python module
                    app/main.py


# FastAPI app

app = FastAPI(title = "MedFlow AI")

- create a FastAPI application object in memory
- note it's not a simple python object because it will hold the configuration and routing information for your web application.

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


