"""
Analytics Service - Main FastAPI Application

Provides analytics and metrics endpoints:
- GET /analytics/summary - Get complete analytics summary
- GET /analytics/applications - Get application statistics
- GET /analytics/metrics/* - Get specific metrics
- GET /analytics/trends/* - Get trend data
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from .routes import analytics_router
from .dependencies import init_db

load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Analytics Service",
    description="Analytics and metrics service for Job Search AI Agent",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analytics_router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


@app.get("/")
def root():
    """Health check endpoint."""
    return {"message": "Analytics Service Running", "version": "1.0.0"}


@app.get("/health")
def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "service": "analytics_service",
        "version": "1.0.0"
    }
