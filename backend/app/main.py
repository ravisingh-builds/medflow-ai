from fastapi import FastAPI

app = FastAPI(
    title="MedFlow AI",
    version="0.1.0",
    description="AI-powered Patient Acquisition Platform"
)


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