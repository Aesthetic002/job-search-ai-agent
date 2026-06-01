"""
Resume Service (Port 8003)
FastAPI microservice for resume upload, parsing, and AI-powered analysis.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.resume_routes import router as resume_router

app = FastAPI(
    title="Resume Service",
    description="Handles resume uploads to Azure, text extraction, AI parsing, and ATS scoring.",
    version="1.0.0"
)

# CORS — allow Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the resume router
app.include_router(resume_router)


@app.get("/")
def root():
    return {
        "message": "Resume Service Running",
        "version": "1.0.0",
        "endpoints": {
            "upload": "POST /resumes/upload",
            "list": "GET /resumes/",
            "get": "GET /resumes/{resume_id}",
            "analyze": "POST /resumes/{resume_id}/analyze",
            "score": "POST /resumes/{resume_id}/score",
            "download": "GET /resumes/{resume_id}/download",
            "delete": "DELETE /resumes/{resume_id}",
            "reparse": "PUT /resumes/{resume_id}/reparse",
        }
    }
