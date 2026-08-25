from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator


class EducationLevel(str, Enum):
    LYCEE = "lycee"
    LICENCE = "licence"
    MASTER = "master"
    DOCTORAT = "doctorat"
    AUTRE = "autre"


class CareerObjective(str, Enum):
    STAGE = "stage"
    EMPLOI = "emploi"
    CONCOURS = "concours"
    SOUTENANCE = "soutenance"
    AUTRE = "autre"


class PreferredLanguage(str, Enum):
    FR = "fr"
    EN = "en"


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: Optional[bool] = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    education_level: Optional[str] = None
    field: Optional[str] = None
    objective: Optional[str] = None
    preferred_language: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserProfileResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    education_level: Optional[str] = None
    field: Optional[str] = None
    objective: Optional[str] = None
    preferred_language: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    education_level: Optional[EducationLevel] = None
    field: Optional[str] = Field(None, max_length=255)
    objective: Optional[CareerObjective] = None
    preferred_language: Optional[PreferredLanguage] = None

    @field_validator("first_name", "last_name", "field", mode="before")
    @classmethod
    def empty_str_to_none(cls, value: object) -> object:
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None
        return value
