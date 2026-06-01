"""
Resume upload and management API endpoints.
Handles file uploads to Azure Blob Storage and stores metadata in Firestore.
Includes AI-powered resume analysis and ATS scoring using Groq LLaMA 3.3 70B.
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, Path, Body
from google.cloud.firestore_v1 import Client as FirestoreClient
from google.cloud.firestore import SERVER_TIMESTAMP
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# Import services
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.resume_file_service import ResumeFileService, upload_and_parse_resume
from backend.auth_service.dependencies import get_db, get_current_user

# Import AI modules
from agent.resume_parser import parse_resume_to_dict
from agent.ats_scoring import score_resume_to_dict

router = APIRouter(prefix="/resumes", tags=["Resumes"])


class ATSScoreRequest(BaseModel):
    """Request body for ATS scoring endpoint."""
    job_description: str = Field(..., min_length=50, description="Full job description text to score the resume against")


class ResumeMetadata(BaseModel):
    """Resume metadata model."""
    resume_id: str
    user_id: str
    file_name: str
    file_path: str
    file_size: int
    file_type: str
    parsed_text: str
    uploaded_at: str


class ResumeListResponse(BaseModel):
    """Response model for listing resumes."""
    resumes: List[Dict[str, Any]]
    total: int


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(..., description="Resume file (PDF, DOCX, TXT)"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: FirestoreClient = Depends(get_db)
):
    """
    Upload a resume file.

    - Uploads file to Azure Blob Storage
    - Parses file content (PDF/DOCX → text)
    - Stores metadata in Firestore
    - Returns resume ID and parsed text
    """
    user_id = current_user['id']

    # Upload and parse resume
    file_metadata = await upload_and_parse_resume(file, user_id)

    # Store metadata in Firestore
    resume_data = {
        'user_id': user_id,
        'file_name': file_metadata['file_name'],
        'file_path': file_metadata['file_path'],
        'file_size': file_metadata['file_size'],
        'file_type': file_metadata['file_type'],
        'blob_url': file_metadata['blob_url'],
        'parsed_text': file_metadata['parsed_text'],
        'uploaded_at': SERVER_TIMESTAMP,
        'updated_at': SERVER_TIMESTAMP
    }

    # Create document with custom ID
    resume_ref = db.collection('resumes').document(file_metadata['resume_id'])
    resume_ref.set(resume_data)

    return {
        "message": "Resume uploaded successfully",
        "resume_id": file_metadata['resume_id'],
        "file_name": file_metadata['file_name'],
        "file_size": file_metadata['file_size'],
        "parsed_text_length": len(file_metadata['parsed_text'])
    }


@router.get("/", response_model=ResumeListResponse)
async def list_resumes(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: FirestoreClient = Depends(get_db)
):
    """
    List all resumes for the current user.
    """
    user_id = current_user['id']

    # Query Firestore
    resumes_ref = db.collection('resumes')
    query = resumes_ref.where('user_id', '==', user_id).order_by('uploaded_at', direction='DESCENDING')
    docs = query.stream()

    resumes = []
    for doc in docs:
        resume_data = doc.to_dict()
        resume_data['resume_id'] = doc.id
        # Don't include full parsed_text in list (too large)
        if 'parsed_text' in resume_data:
            resume_data['parsed_text_length'] = len(resume_data['parsed_text'])
            del resume_data['parsed_text']
        resumes.append(resume_data)

    return ResumeListResponse(
        resumes=resumes,
        total=len(resumes)
    )


@router.get("/{resume_id}")
async def get_resume(
    resume_id: str = Path(..., description="Resume ID"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: FirestoreClient = Depends(get_db)
):
    """
    Get full resume metadata including parsed text.
    """
    user_id = current_user['id']

    # Get from Firestore
    resume_ref = db.collection('resumes').document(resume_id)
    resume_doc = resume_ref.get()

    if not resume_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    resume_data = resume_doc.to_dict()

    # Check ownership
    if resume_data.get('user_id') != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resume"
        )

    resume_data['resume_id'] = resume_id
    return resume_data


@router.get("/{resume_id}/download")
async def download_resume(
    resume_id: str = Path(..., description="Resume ID"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: FirestoreClient = Depends(get_db)
):
    """
    Get a temporary download URL for the resume file.

    Returns a signed URL valid for 24 hours.
    """
    user_id = current_user['id']

    # Get from Firestore
    resume_ref = db.collection('resumes').document(resume_id)
    resume_doc = resume_ref.get()

    if not resume_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    resume_data = resume_doc.to_dict()

    # Check ownership
    if resume_data.get('user_id') != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resume"
        )

    # Generate signed URL
    download_url = ResumeFileService.get_resume_url(
        blob_name=resume_data['file_path'],
        expiry_hours=24
    )

    return {
        "resume_id": resume_id,
        "file_name": resume_data['file_name'],
        "download_url": download_url,
        "expires_in_hours": 24
    }


@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: str = Path(..., description="Resume ID"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: FirestoreClient = Depends(get_db)
):
    """
    Delete a resume file and its metadata.
    """
    user_id = current_user['id']

    # Get from Firestore
    resume_ref = db.collection('resumes').document(resume_id)
    resume_doc = resume_ref.get()

    if not resume_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    resume_data = resume_doc.to_dict()

    # Check ownership
    if resume_data.get('user_id') != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this resume"
        )

    # Delete from Azure
    ResumeFileService.delete_resume(resume_data['file_path'])

    # Delete from Firestore
    resume_ref.delete()

    return {
        "message": "Resume deleted successfully",
        "resume_id": resume_id
    }


@router.put("/{resume_id}/reparse")
async def reparse_resume(
    resume_id: str = Path(..., description="Resume ID"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: FirestoreClient = Depends(get_db)
):
    """
    Re-parse the resume file to extract text again.

    Useful if parsing failed initially or if parsing logic improved.
    """
    user_id = current_user['id']

    # Get from Firestore
    resume_ref = db.collection('resumes').document(resume_id)
    resume_doc = resume_ref.get()

    if not resume_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    resume_data = resume_doc.to_dict()

    # Check ownership
    if resume_data.get('user_id') != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resume"
        )

    # Download file from Azure
    file_content = ResumeFileService.download_resume(resume_data['file_path'])

    # Parse again
    parsed_text = ResumeFileService.parse_resume(file_content, resume_data['file_type'])

    # Update Firestore
    resume_ref.update({
        'parsed_text': parsed_text,
        'updated_at': SERVER_TIMESTAMP
    })

    return {
        "message": "Resume reparsed successfully",
        "resume_id": resume_id,
        "parsed_text_length": len(parsed_text)
    }


@router.post("/{resume_id}/analyze")
async def analyze_resume(
    resume_id: str = Path(..., description="Resume ID"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: FirestoreClient = Depends(get_db)
):
    """
    AI-powered structured analysis of a resume.

    - Fetches raw parsed text from Firestore.
    - Uses Groq LLaMA 3.3 70B to extract Contact, Education, Experience, and Skills.
    - Saves structured JSON back to the Firestore document under 'structured_data'.
    - Returns the structured resume data.
    """
    user_id = current_user['id']

    # Fetch resume from Firestore
    resume_ref = db.collection('resumes').document(resume_id)
    resume_doc = resume_ref.get()

    if not resume_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    resume_data = resume_doc.to_dict()

    # Ownership check
    if resume_data.get('user_id') != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resume"
        )

    raw_text = resume_data.get('parsed_text', '')
    if not raw_text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Resume has no parsed text. Please upload and parse the resume first."
        )

    # Run AI structured extraction
    try:
        structured_data = parse_resume_to_dict(raw_text)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI resume analysis failed: {str(e)}"
        )

    # Save structured data back to Firestore
    resume_ref.update({
        'structured_data': structured_data,
        'analyzed_at': SERVER_TIMESTAMP,
        'updated_at': SERVER_TIMESTAMP
    })

    return {
        "message": "Resume analyzed successfully",
        "resume_id": resume_id,
        "structured_data": structured_data
    }


@router.post("/{resume_id}/score")
async def score_resume(
    resume_id: str = Path(..., description="Resume ID"),
    body: ATSScoreRequest = Body(...),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: FirestoreClient = Depends(get_db)
):
    """
    ATS compatibility scoring of a resume against a specific job description.

    - Accepts a job description in the request body.
    - Fetches the resume's raw text from Firestore.
    - Uses Groq LLaMA 3.3 70B to produce a detailed ATS report:
        - Overall score (0-100)
        - Keyword matches and missing keywords
        - Experience relevance summary
        - Formatting feedback
        - Top actionable recommendations
    - Saves the ATS report to Firestore.
    - Returns the full ATS score report.
    """
    user_id = current_user['id']

    # Fetch resume from Firestore
    resume_ref = db.collection('resumes').document(resume_id)
    resume_doc = resume_ref.get()

    if not resume_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    resume_data = resume_doc.to_dict()

    # Ownership check
    if resume_data.get('user_id') != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resume"
        )

    raw_text = resume_data.get('parsed_text', '')
    if not raw_text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Resume has no parsed text. Please upload and parse the resume first."
        )

    # Run ATS scoring
    try:
        ats_report = score_resume_to_dict(raw_text, body.job_description)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ATS scoring failed: {str(e)}"
        )

    # Optionally persist the last ATS report in Firestore
    resume_ref.update({
        'last_ats_report': ats_report,
        'last_ats_score': ats_report.get('overall_score'),
        'updated_at': SERVER_TIMESTAMP
    })

    return {
        "message": "ATS scoring completed",
        "resume_id": resume_id,
        "ats_report": ats_report
    }
