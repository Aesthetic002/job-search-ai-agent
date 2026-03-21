"""
Pydantic schemas for auth_service request/response validation.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr


class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    full_name: Optional[str] = None


class UserLogin(UserBase):
    """Schema for user login."""
    password: str


class UserResponse(UserBase):
    """Schema for user response (excludes password)."""
    id: str  # Firestore uses string document IDs
    full_name: Optional[str] = None
    created_at: Optional[datetime] = None  # Optional for Firestore SERVER_TIMESTAMP

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserInDB(UserBase):
    """Schema for user stored in database (includes hashed password)."""
    id: str
    hashed_password: str
    full_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for decoded token data."""
    user_id: Optional[str] = None  # Firestore uses string IDs
    email: Optional[str] = None


class RegisterResponse(BaseModel):
    """Schema for registration response."""
    user_id: str  # Firestore uses string IDs
    message: str = "User registered successfully"


class MessageResponse(BaseModel):
    """Generic message response schema."""
    message: str
