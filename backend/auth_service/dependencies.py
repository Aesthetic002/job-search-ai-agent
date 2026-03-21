"""
Dependencies for auth_service including Firestore client and JWT authentication.
"""
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
from google.cloud.firestore_v1 import Client as FirestoreClient

# Import config module from project root
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import get_firestore_client

from .schemas import TokenData, UserInDB

load_dotenv()

# JWT configuration
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))  # 24 hours

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Firestore client (lazy initialization)
_firestore_client: Optional[FirestoreClient] = None


def get_db() -> FirestoreClient:
    """Dependency to get Firestore client."""
    global _firestore_client
    if _firestore_client is None:
        _firestore_client = get_firestore_client()
    return _firestore_client


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[TokenData]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        if user_id is None:
            return None
        return TokenData(user_id=user_id, email=email)
    except JWTError:
        return None


def get_user_from_firestore(db: FirestoreClient, user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get user data from Firestore by user ID.

    Args:
        db: Firestore client
        user_id: User document ID

    Returns:
        User data dict or None if not found
    """
    user_ref = db.collection('users').document(user_id)
    user_doc = user_ref.get()

    if user_doc.exists:
        user_data = user_doc.to_dict()
        user_data['id'] = user_doc.id
        return user_data
    return None


def get_user_by_email(db: FirestoreClient, email: str) -> Optional[Dict[str, Any]]:
    """
    Get user data from Firestore by email.

    Args:
        db: Firestore client
        email: User email

    Returns:
        User data dict or None if not found
    """
    from google.cloud.firestore_v1.base_query import FieldFilter

    try:
        users_ref = db.collection('users')
        query = users_ref.where(filter=FieldFilter('email', '==', email)).limit(1)
        docs = list(query.stream())

        if docs:
            doc = docs[0]
            user_data = doc.to_dict()
            user_data['id'] = doc.id
            return user_data

        return None
    except Exception as e:
        print(f"[ERROR] get_user_by_email: {e}")
        return None


def create_user_in_firestore(
    db: FirestoreClient,
    email: str,
    hashed_password: str,
    full_name: str
) -> Dict[str, Any]:
    """
    Create a new user in Firestore.

    Args:
        db: Firestore client
        email: User email
        hashed_password: Bcrypt hashed password
        full_name: User's full name

    Returns:
        Created user data with document ID
    """
    import uuid
    from google.cloud.firestore import SERVER_TIMESTAMP

    user_data = {
        'email': email,
        'hashed_password': hashed_password,
        'full_name': full_name,
        'created_at': SERVER_TIMESTAMP,
        'updated_at': SERVER_TIMESTAMP
    }

    # Create with auto-generated ID or use UUID
    user_ref = db.collection('users').document()
    user_ref.set(user_data)

    # Return user with ID
    user_data['id'] = user_ref.id
    return user_data


def update_user_in_firestore(
    db: FirestoreClient,
    user_id: str,
    update_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Update user data in Firestore.

    Args:
        db: Firestore client
        user_id: User document ID
        update_data: Fields to update

    Returns:
        Updated user data or None if not found
    """
    from google.cloud.firestore import SERVER_TIMESTAMP

    user_ref = db.collection('users').document(user_id)

    # Check if user exists
    if not user_ref.get().exists:
        return None

    # Add updated timestamp
    update_data['updated_at'] = SERVER_TIMESTAMP

    # Update the document
    user_ref.update(update_data)

    # Return updated user
    return get_user_from_firestore(db, user_id)


def delete_user_from_firestore(db: FirestoreClient, user_id: str) -> bool:
    """
    Delete user from Firestore.

    Args:
        db: Firestore client
        user_id: User document ID

    Returns:
        True if deleted, False if not found
    """
    user_ref = db.collection('users').document(user_id)

    if not user_ref.get().exists:
        return False

    user_ref.delete()
    return True


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: FirestoreClient = Depends(get_db)
) -> Dict[str, Any]:
    """Get the current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = decode_token(token)
    if token_data is None:
        raise credentials_exception

    user = get_user_from_firestore(db, token_data.user_id)
    if user is None:
        raise credentials_exception

    return user


def init_db():
    """
    Initialize Firestore database.

    Note: Firestore is schemaless, so no table creation needed.
    This function ensures Firebase is initialized and creates indexes if needed.
    """
    try:
        db = get_firestore_client()
        print("[OK] Firestore initialized successfully")

        # Optionally create a test document to verify connection
        # db.collection('_test').document('init').set({'initialized': True})

    except Exception as e:
        print(f"[WARN] Firestore initialization warning: {e}")
