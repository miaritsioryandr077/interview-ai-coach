from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict
from app.models.session import SessionStatus
from app.schemas.question import QuestionResponse
from app.schemas.response import ResponseResponse


class SessionResponse(BaseModel):
    """Détail d'une session : questions ordonnées et réponses enregistrées."""

    id: int
    context_id: int
    user_id: int
    status: SessionStatus
    started_at: datetime
    ended_at: Optional[datetime] = None
    total_questions: int = 0
    questions: List[QuestionResponse] = []
    responses: List[ResponseResponse] = []

    model_config = ConfigDict(from_attributes=True)
