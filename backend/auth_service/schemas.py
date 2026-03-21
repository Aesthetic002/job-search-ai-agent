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
    id: int
    full_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for decoded token data."""
    user_id: Optional[int] = None
    email: Optional[str] = None


class RegisterResponse(BaseModel):
    """Schema for registration response."""
    user_id: int
    message: str = "User registered successfully"


class MessageResponse(BaseModel):
    """Generic message response schema."""
    message: str
