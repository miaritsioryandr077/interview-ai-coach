from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.document import DocumentResponse

class ContextBase(BaseModel):
    cv_id: int
    job_id: int
    notes: Optional[str] = None

class ContextCreate(ContextBase):
    pass

class ContextCreateDB(ContextBase):
    user_id: int

class ContextResponse(ContextBase):
    id: int
    user_id: int
    created_at: datetime
    cv: Optional[DocumentResponse] = None
    job: Optional[DocumentResponse] = None

    model_config = ConfigDict(from_attributes=True)