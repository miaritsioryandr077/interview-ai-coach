from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class ResponseBase(BaseModel):
    question_id: int
    text: str


class ResponseCreate(ResponseBase):
    """Payload envoyé par le frontend pour enregistrer une réponse."""

    @field_validator("text")
    @classmethod
    def text_not_blank(cls, value: str) -> str:
        if value is None or not value.strip():
            raise ValueError("Le texte de la réponse ne peut pas être vide.")
        return value


class ResponseCreateDB(ResponseBase):
    session_id: int


class ResponseResponse(ResponseBase):
    id: int
    session_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
