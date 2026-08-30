import os
import uuid
import shutil
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.document import DocumentType
from app.schemas.document import DocumentCreate, DocumentResponse
from app.repositories.document import document_repository
from app.core.config import settings
import mimetypes
from app.services.pdf_extractor import extract_text_from_pdf

class DocumentService:
    ALLOWED_MIME_TYPES = ["application/pdf"]
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

    def validate_file(self, file: UploadFile) -> None:
        """Validate uploaded file: size, type, and extension."""
        # Check MIME type
        if file.content_type not in self.ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type. Allowed: {', '.join(self.ALLOWED_MIME_TYPES)}"
            )
        
        # Check file extension
        filename = file.filename or ""
        if not filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must have .pdf extension"
            )
        
        # Check file size (read a chunk to check)
        file.file.seek(0, 2)  # Seek to end
        size = file.file.tell()
        file.file.seek(0)  # Reset position
        if size > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {self.MAX_FILE_SIZE // (1024*1024)}MB"
            )

    def save_file(self, file: UploadFile, user_id: int, doc_type: DocumentType) -> Tuple[str, str, str]:
        """Save uploaded file to disk and return stored_filename, file_path, and mime_type."""
        # Generate unique filename
        file_ext = os.path.splitext(file.filename or "unknown.pdf")[1]
        stored_filename = f"{uuid.uuid4()}{file_ext}"
        
        # Create user-specific directory
        user_dir = os.path.join(settings.UPLOAD_DIR, str(user_id), doc_type.value)
        os.makedirs(user_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(user_dir, stored_filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        return stored_filename, file_path, file.content_type or "application/pdf"

    def create_document(
        self,
        db: Session,
        user: User,
        file: UploadFile,
        doc_type: DocumentType
    ) -> DocumentResponse:
        """Process and save uploaded document."""
        # Validate
        self.validate_file(file)
        
        # Save physically
        stored_filename, file_path, mime_type = self.save_file(file, user.id, doc_type)
        
        # Extraction du texte
        extracted_text = extract_text_from_pdf(file_path)
        
        # Create DB record
        doc_in = DocumentCreate(
            user_id=user.id,
            document_type=doc_type,
            original_filename=file.filename or "unknown.pdf",
            stored_filename=stored_filename,
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            mime_type=mime_type,
            extracted_text=extracted_text,
        )
        
        db_document = document_repository.create(db, doc_in)
        return DocumentResponse.model_validate(db_document)

    def get_user_documents(self, db: Session, user: User) -> list[DocumentResponse]:
        """Get all documents for a user."""
        documents = document_repository.get_by_user_id(db, user.id)
        return [DocumentResponse.model_validate(doc) for doc in documents]

    def delete_document(self, db: Session, user: User, document_id: int) -> None:
        """Delete a document (physical + DB)."""
        document = document_repository.get_by_id_and_user(db, document_id, user.id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found or you don't have permission"
            )
        
        # Delete physical file
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
            # Try to remove empty directory
            try:
                os.rmdir(os.path.dirname(document.file_path))
            except OSError:
                pass  # Directory not empty
        
        # Delete DB record
        document_repository.delete(db, document)

document_service = DocumentService()