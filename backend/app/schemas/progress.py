from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class CriteriaAverages(BaseModel):
    pertinence: Optional[float] = None
    structure: Optional[float] = None
    clarte: Optional[float] = None
    vocabulaire: Optional[float] = None


class EvolutionItem(BaseModel):
    session_id: int
    date: datetime
    overall_score: float
    preparation_title: str


class ProgressResponse(BaseModel):
    total_completed: int
    total_analyzed: int
    average_overall: Optional[float] = None
    average_by_criterion: CriteriaAverages
    evolution: List[EvolutionItem] = []

    model_config = ConfigDict(from_attributes=True)


class PreparationProgressResponse(ProgressResponse):
    preparation_id: int