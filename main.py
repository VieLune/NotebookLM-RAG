import uvicorn
from fastapi import FastAPI
from app.core.config import settings
from app.api.api import api_router

app = FastAPI(
    title="GeminiDocAgent API",
    description="A NotebookLM-like document analysis agent using Gemini and LangChain",
    version="0.1.0",
    debug=settings.config.get("server", {}).get("debug", False)
)

@app.get("/")
def read_root():
    return {"message": "Welcome to GeminiDocAgent API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.config.get("server", {}).get("host", "0.0.0.0"),
        port=settings.config.get("server", {}).get("port", 8000),
        reload=True
    )

