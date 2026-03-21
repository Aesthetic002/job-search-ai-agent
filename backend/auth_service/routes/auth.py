"""
Authentication routes for user registration and login.
Uses Firestore for user data storage.
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from google.cloud.firestore_v1 import Client as FirestoreClient

from ..schemas import (
    UserCreate,
    UserLogin,
    Token,
    RegisterResponse,
    MessageResponse
)
from ..dependencies import (
    get_db,
    verify_password,
    get_password_hash,
    create_access_token,
    get_user_by_email,
    create_user_in_firestore,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: FirestoreClient = Depends(get_db)):
    """
    Register a new user.

    - **email**: Valid email address (must be unique)
    - **password**: Minimum 8 characters
    - **full_name**: Optional full name
    """
    # Check if user already exists
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user with hashed password
    hashed_password = get_password_hash(user_data.password)
    new_user = create_user_in_firestore(
        db=db,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name or ""
    )

    return RegisterResponse(user_id=new_user['id'])


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: FirestoreClient = Depends(get_db)):
    """
    Login with email and password to receive JWT access token.

    - **email**: Registered email address
    - **password**: User password
    """
    # Find user by email
    user = get_user_by_email(db, user_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not verify_password(user_data.password, user['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user['id']), "email": user['email']},
        expires_delta=access_token_expires
    )

    return Token(access_token=access_token)


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: FirestoreClient = Depends(get_db)
):
    """
    OAuth2 compatible token endpoint.
    Use this for Swagger UI authentication.
    """
    user = get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user['id']), "email": user['email']},
        expires_delta=access_token_expires
    )

    return Token(access_token=access_token)
