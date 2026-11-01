from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class CriterionScores(BaseModel):
    pertinence: float = Field(ge=0, le=10)
    structure: float = Field(ge=0, le=10)
    clarte: float = Field(ge=0, le=10)
    vocabulaire: float = Field(ge=0, le=10)


class ResponseAnalysis(BaseModel):
    question_id: int
    question: str
    answered: bool
    score: Optional[float] = Field(default=None, ge=0, le=10)
    feedback: Optional[str] = None
    improved_answer: Optional[str] = None


class AnalysisResponse(BaseModel):
    version: int = Field(ge=1)
    overall_score: float = Field(ge=0, le=10)
    criteria: CriterionScores
    strengths: List[str] = []
    weaknesses: List[str] = []
    advice: List[str] = []
    responses: List[ResponseAnalysis] = []
    model: str
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)