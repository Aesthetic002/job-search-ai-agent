"""
Dependencies for analytics_service including Firestore client.
"""
import os
from typing import Optional
from dotenv import load_dotenv
from google.cloud.firestore_v1 import Client as FirestoreClient

# Import config module from project root
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import get_firestore_client

load_dotenv()

# Firestore client (lazy initialization)
_firestore_client: Optional[FirestoreClient] = None


def get_db() -> FirestoreClient:
    """Dependency to get Firestore client."""
    global _firestore_client
    if _firestore_client is None:
        _firestore_client = get_firestore_client()
    return _firestore_client


def init_db():
    """
    Initialize Firestore database.

    Note: Firestore is schemaless, so no table creation needed.
    This function ensures Firebase is initialized.
    """
    try:
        db = get_firestore_client()
        print("[OK] Firestore initialized successfully for analytics service")
    except Exception as e:
        print(f"[WARN] Firestore initialization warning: {e}")
