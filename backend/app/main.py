import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=True)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Misinformation Cascade Tracker API",
    description="API for CSV validation, misinformation analysis, cascade tracking, and risk assessment.",
    version="1.0.0",
)

from app.api.routes import router

app.include_router(router, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "Misinformation Cascade Tracker API is running",
        "status": "healthy",
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
