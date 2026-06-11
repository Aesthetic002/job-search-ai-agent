"""
Auth Service - Main FastAPI Application

Provides authentication and user management endpoints:
- POST /auth/register - Register new user
- POST /auth/login - Login and get JWT token
- GET /users/me - Get current user profile
- PUT /users/me - Update user profile
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from .routes import auth_router, users_router, applications_router
from .dependencies import init_db

load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Auth Service",
    description="Authentication and user management service for Job Search AI Agent",
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
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(applications_router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


@app.get("/")
def root():
    """Health check endpoint."""
    return {"message": "Auth Service Running", "version": "1.0.0"}


@app.get("/health")
def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "service": "auth_service",
        "version": "1.0.0"
    }
