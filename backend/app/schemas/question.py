from datetime import datetime
from pydantic import BaseModel, ConfigDict

class QuestionBase(BaseModel):
    text: str
    category: str
    difficulty: str
    order_index: int
    expected_duration_seconds: int

class QuestionCreate(QuestionBase):
    context_id: int

class QuestionResponse(QuestionBase):
    id: int
    context_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class GenerateQuestionsRequest(BaseModel):
    # Potential parameters like number of questions, etc.
    pass