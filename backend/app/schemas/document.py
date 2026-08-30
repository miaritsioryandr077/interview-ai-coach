from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from enum import Enum

class DocumentType(str, Enum):
    CV = "cv"
    JOB_OFFER = "job_offer"

class DocumentBase(BaseModel):
    document_type: DocumentType
    original_filename: str
    file_size: int
    mime_type: str

class DocumentCreate(DocumentBase):
    user_id: int
    stored_filename: str
    file_path: str
    extracted_text: Optional[str] = None

class DocumentResponse(DocumentBase):
    id: int
    user_id: int
    uploaded_at: datetime
    extracted_text: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class DocumentUploadResponse(BaseModel):
    id: int
    original_filename: str
    document_type: DocumentType
    file_size: int
    uploaded_at: datetime
    message: str