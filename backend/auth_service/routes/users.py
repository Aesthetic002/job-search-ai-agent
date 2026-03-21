"""
User management routes for profile operations.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..models import User
from ..schemas import UserResponse, UserUpdate, MessageResponse
from ..dependencies import get_db, get_current_user, get_password_hash

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get the current authenticated user's profile.

    Requires valid JWT token in Authorization header.
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the current authenticated user's profile.

    - **full_name**: Optional new full name
    - **email**: Optional new email (must be unique)
    """
    # Check if new email is already taken
    if user_update.email and user_update.email != current_user.email:
        existing_user = db.query(User).filter(User.email == user_update.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = user_update.email

    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name

    db.commit()
    db.refresh(current_user)

    return current_user


@router.delete("/me", response_model=MessageResponse)
async def delete_current_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete the current authenticated user's account.

    This action is irreversible.
    """
    db.delete(current_user)
    db.commit()

    return MessageResponse(message="User account deleted successfully")


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a user's public profile by ID.

    Requires authentication.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user
