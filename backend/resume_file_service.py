"""
Resume file handling service using Azure Blob Storage.
Handles upload, download, and parsing of resume files (PDF, DOCX).
"""
import os
import io
from typing import Optional, Dict, Any, List
from fastapi import UploadFile, HTTPException, status
from datetime import datetime

# Import config
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    upload_file_to_azure,
    download_file_from_azure,
    delete_file_from_azure,
    get_blob_url
)

# File parsing imports
import PyPDF2
import docx
from PIL import Image
import pdf2image


class ResumeFileService:
    """Service for handling resume file operations with Azure Blob Storage."""

    ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    @staticmethod
    def validate_file(file: UploadFile) -> None:
        """
        Validate uploaded file.

        Args:
            file: Uploaded file object

        Raises:
            HTTPException: If file is invalid
        """
        # Check file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ResumeFileService.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file_ext} not allowed. Allowed types: {', '.join(ResumeFileService.ALLOWED_EXTENSIONS)}"
            )

        # Check file size (FastAPI does this automatically, but double check)
        if file.size and file.size > ResumeFileService.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum of {ResumeFileService.MAX_FILE_SIZE / 1024 / 1024}MB"
            )

    @staticmethod
    async def upload_resume(
        file: UploadFile,
        user_id: str,
        resume_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload resume file to Azure Blob Storage.

        Args:
            file: Uploaded file
            user_id: User ID
            resume_id: Optional resume ID (generates new if not provided)

        Returns:
            Dictionary with file metadata
        """
        # Validate file
        ResumeFileService.validate_file(file)

        # Generate resume ID if not provided
        if not resume_id:
            import uuid
            resume_id = str(uuid.uuid4())

        # Generate blob name
        file_ext = os.path.splitext(file.filename)[1].lower()
        blob_name = f"resumes/{user_id}/{resume_id}{file_ext}"

        # Read file content
        file_content = await file.read()

        # Determine content type
        content_types = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.txt': 'text/plain'
        }
        content_type = content_types.get(file_ext, 'application/octet-stream')

        # Upload to Azure
        try:
            blob_url = upload_file_to_azure(
                file_data=file_content,
                blob_name=blob_name,
                content_type=content_type
            )

            return {
                'resume_id': resume_id,
                'user_id': user_id,
                'file_name': file.filename,
                'file_path': blob_name,
                'file_size': len(file_content),
                'file_type': file_ext,
                'blob_url': blob_url,
                'uploaded_at': datetime.utcnow()
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file: {str(e)}"
            )

    @staticmethod
    def download_resume(blob_name: str) -> bytes:
        """
        Download resume file from Azure Blob Storage.

        Args:
            blob_name: Blob path in Azure

        Returns:
            File content as bytes
        """
        try:
            return download_file_from_azure(blob_name)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Failed to download file: {str(e)}"
            )

    @staticmethod
    def delete_resume(blob_name: str) -> bool:
        """
        Delete resume file from Azure Blob Storage.

        Args:
            blob_name: Blob path in Azure

        Returns:
            True if deleted successfully
        """
        try:
            return delete_file_from_azure(blob_name)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete file: {str(e)}"
            )

    @staticmethod
    def get_resume_url(blob_name: str, expiry_hours: int = 24) -> str:
        """
        Get temporary signed URL for resume download.

        Args:
            blob_name: Blob path in Azure
            expiry_hours: URL expiry time in hours

        Returns:
            Signed URL
        """
        try:
            return get_blob_url(blob_name, expiry_hours=expiry_hours)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate download URL: {str(e)}"
            )

    @staticmethod
    def parse_pdf(file_content: bytes) -> str:
        """
        Extract text from PDF file.

        Args:
            file_content: PDF file content as bytes

        Returns:
            Extracted text
        """
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"

            return text.strip()

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f "Failed to parse PDF: {str(e)}"
            )

    @staticmethod
    def parse_docx(file_content: bytes) -> str:
        """
        Extract text from DOCX file.

        Args:
            file_content: DOCX file content as bytes

        Returns:
            Extracted text
        """
        try:
            docx_file = io.BytesIO(file_content)
            doc = docx.Document(docx_file)

            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"

            return text.strip()

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to parse DOCX: {str(e)}"
            )

    @staticmethod
    def parse_resume(file_content: bytes, file_type: str) -> str:
        """
        Parse resume file and extract text.

        Args:
            file_content: File content as bytes
            file_type: File extension (.pdf, .docx, .txt)

        Returns:
            Extracted text
        """
        if file_type == '.pdf':
            return ResumeFileService.parse_pdf(file_content)
        elif file_type in ['.docx', '.doc']:
            return ResumeFileService.parse_docx(file_content)
        elif file_type == '.txt':
            return file_content.decode('utf-8')
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file_type}"
            )


# Example usage and helper functions

async def upload_and_parse_resume(
    file: UploadFile,
    user_id: str
) -> Dict[str, Any]:
    """
    Upload resume to Azure and extract text.

    Args:
        file: Uploaded resume file
        user_id: User ID

    Returns:
        Dictionary with file metadata and parsed text
    """
    # Upload file
    file_metadata = await ResumeFileService.upload_resume(file, user_id)

    # Download and parse
    file_content = ResumeFileService.download_resume(file_metadata['file_path'])
    parsed_text = ResumeFileService.parse_resume(file_content, file_metadata['file_type'])

    # Add parsed text to metadata
    file_metadata['parsed_text'] = parsed_text

    return file_metadata
