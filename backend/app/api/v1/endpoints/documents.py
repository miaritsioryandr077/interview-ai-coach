from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.document import DocumentType
from app.schemas.document import DocumentResponse, DocumentUploadResponse
from app.services.document import document_service

router = APIRouter()

@router.post("/upload/cv", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_cv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a CV (PDF) for the authenticated user."""
    if not file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided")
    
    doc = document_service.create_document(db, current_user, file, DocumentType.CV)
    
    return DocumentUploadResponse(
        id=doc.id,
        original_filename=doc.original_filename,
        document_type=doc.document_type,
        file_size=doc.file_size,
        uploaded_at=doc.uploaded_at,
        message="CV uploaded successfully"
    )

@router.get("/", response_model=List[DocumentResponse])
def get_my_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all documents of the authenticated user."""
    return document_service.get_user_documents(db, current_user)

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a document (only if it belongs to the authenticated user)."""
    document_service.delete_document(db, current_user, document_id)