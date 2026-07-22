"""
AI Resume Screening System — FastAPI application entrypoint.

Run with:
    uvicorn app.main:app --reload

This also serves the static frontend (single HTML file) at "/", so you
only need to run this one process to use the whole app.
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.database import Base, engine
from app.models import models  # noqa: F401  (ensures models are registered)
from app.routers import jobs, candidates

# Create DB tables if they don't exist yet
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Resume Screening System",
    description="Upload job descriptions and resumes; get AI-ranked candidates.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router)
app.include_router(candidates.router)

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


# Serve the frontend's single-page app at root
if FRONTEND_DIR.exists():
    @app.get("/")
    def serve_frontend():
        return FileResponse(FRONTEND_DIR / "index.html")

    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
