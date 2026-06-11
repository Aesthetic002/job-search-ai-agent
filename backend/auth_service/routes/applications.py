"""
Applications Router — Firestore-backed Kanban board persistence.

Endpoints:
  GET    /applications        — List all applications for the current user
  POST   /applications        — Create a new application
  PATCH  /applications/{id}/stage — Move an application to a new stage
  DELETE /applications/{id}   — Delete an application
"""
import sys
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from backend.auth_service.dependencies import get_db, get_current_user

router = APIRouter(prefix="/applications", tags=["Applications"])

VALID_STAGES = {"applied", "screening", "interviewing", "offer", "rejected", "archived"}


# ─── Pydantic models ──────────────────────────────────────────────────────────

class ApplicationCreate(BaseModel):
    jobTitle: str
    company: str
    location: Optional[str] = None
    stage: str = "applied"
    source: str = "other"
    matchScore: Optional[int] = None
    notes: Optional[str] = None
    nextAction: Optional[str] = None
    url: Optional[str] = None


class StageUpdate(BaseModel):
    stage: str


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _doc_to_dict(doc) -> dict:
    """Convert a Firestore document snapshot to a plain dict with id field."""
    data = doc.to_dict()
    data["id"] = doc.id
    # Convert Firestore Timestamps to ISO strings
    if "appliedAt" in data and hasattr(data["appliedAt"], "isoformat"):
        data["appliedAt"] = data["appliedAt"].isoformat()
    return data


# ─── Routes ───────────────────────────────────────────────────────────────────

@router.get("/", response_model=List[Dict[str, Any]])
async def list_applications(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db=Depends(get_db),
):
    """Return all applications for the authenticated user, newest first."""
    user_id = current_user["id"]
    docs = (
        db.collection("applications")
        .where("user_id", "==", user_id)
        .order_by("appliedAt", direction="DESCENDING")
        .stream()
    )
    return [_doc_to_dict(d) for d in docs]


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_application(
    body: ApplicationCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db=Depends(get_db),
):
    """Create a new application and save it to Firestore."""
    if body.stage not in VALID_STAGES:
        raise HTTPException(status_code=400, detail=f"Invalid stage '{body.stage}'. Valid: {VALID_STAGES}")

    user_id = current_user["id"]
    data = {
        **body.model_dump(),
        "user_id": user_id,
        "appliedAt": datetime.now(timezone.utc),
    }

    ref = db.collection("applications").document()
    ref.set(data)

    return {"id": ref.id, **body.model_dump(), "appliedAt": datetime.now(timezone.utc).isoformat()}


@router.patch("/{application_id}/stage")
async def update_stage(
    application_id: str,
    body: StageUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db=Depends(get_db),
):
    """Move an application to a different Kanban stage."""
    if body.stage not in VALID_STAGES:
        raise HTTPException(status_code=400, detail=f"Invalid stage '{body.stage}'.")

    user_id = current_user["id"]
    ref = db.collection("applications").document(application_id)
    doc = ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Application not found.")
    if doc.to_dict().get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized.")

    ref.update({"stage": body.stage})
    return {"id": application_id, "stage": body.stage, "message": "Stage updated."}


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(
    application_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db=Depends(get_db),
):
    """Permanently delete an application."""
    user_id = current_user["id"]
    ref = db.collection("applications").document(application_id)
    doc = ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Application not found.")
    if doc.to_dict().get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized.")

    ref.delete()
