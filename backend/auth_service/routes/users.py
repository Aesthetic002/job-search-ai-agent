"""
User management routes for profile operations.
Uses Firestore for user data storage.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from google.cloud.firestore_v1 import Client as FirestoreClient
from typing import List, Dict, Any

from ..schemas import UserResponse, UserUpdate, MessageResponse
from ..dependencies import (
    get_db,
    get_current_user,
    get_password_hash,
    get_user_from_firestore,
    get_user_by_email,
    update_user_in_firestore,
    delete_user_from_firestore
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get the current authenticated user's profile.

    Requires valid JWT token in Authorization header.
    """
    return UserResponse(**current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: FirestoreClient = Depends(get_db)
):
    """
    Update the current authenticated user's profile.

    - **full_name**: Optional new full name
    - **email**: Optional new email (must be unique)
    """
    update_data = {}

    # Check if new email is already taken
    if user_update.email and user_update.email != current_user['email']:
        existing_user = get_user_by_email(db, user_update.email)
        if existing_user and existing_user['id'] != current_user['id']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        update_data['email'] = user_update.email

    if user_update.full_name is not None:
        update_data['full_name'] = user_update.full_name

    # Update user in Firestore
    if update_data:
        updated_user = update_user_in_firestore(db, current_user['id'], update_data)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return UserResponse(**updated_user)

    return UserResponse(**current_user)


@router.delete("/me", response_model=MessageResponse)
async def delete_current_user(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: FirestoreClient = Depends(get_db)
):
    """
    Delete the current authenticated user's account.

    This action is irreversible.
    """
    success = delete_user_from_firestore(db, current_user['id'])
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return MessageResponse(message="User account deleted successfully")


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    db: FirestoreClient = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get a user's public profile by ID.

    Requires authentication.
    """
    user = get_user_from_firestore(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(**user)
