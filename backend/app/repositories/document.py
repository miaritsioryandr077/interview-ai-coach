from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.document import Document
from app.schemas.document import DocumentCreate

class DocumentRepository:
    def create(self, db: Session, document_in: DocumentCreate) -> Document:
        db_document = Document(
            user_id=document_in.user_id,
            document_type=document_in.document_type,
            original_filename=document_in.original_filename,
            stored_filename=document_in.stored_filename,
            file_path=document_in.file_path,
            file_size=document_in.file_size,
            mime_type=document_in.mime_type,
        )
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        return db_document

    def get_by_user_id(self, db: Session, user_id: int) -> List[Document]:
        return db.query(Document).filter(Document.user_id == user_id).order_by(Document.uploaded_at.desc()).all()

    def get_by_id_and_user(self, db: Session, document_id: int, user_id: int) -> Optional[Document]:
        return db.query(Document).filter(Document.id == document_id, Document.user_id == user_id).first()

    def delete(self, db: Session, document: Document) -> None:
        db.delete(document)
        db.commit()

document_repository = DocumentRepository()