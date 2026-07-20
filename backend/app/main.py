from fastapi import FastAPI

from app.api.ai import router as ai_router

app = FastAPI(title="MedFlow AI")

app.include_router(ai_router)


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