from typing import Optional
from pathlib import Path
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "InterviewAI Coach API"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "default_secret_key_change_me_in_production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # PostgreSQL Database Settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "interview_ai_coach"
    
    DATABASE_URL: Optional[str] = None
    
    # Upload Settings
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_MIME_TYPES: list = ["application/pdf"]

    # Réponses vocales (simulation d'entretien à l'oral)
    AUDIO_UPLOAD_DIR: str = "uploads/audio"
    MAX_AUDIO_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_AUDIO_MIME_TYPES: list = [
        "audio/webm",
        "audio/wav",
        "audio/mpeg",
        "audio/ogg",
    ]
    # Modèle Gemini multimodal utilisé pour la transcription audio.
    GEMINI_TRANSCRIPTION_MODEL: str = "gemini-2.0-flash"
    TRANSCRIPTION_TIMEOUT_SECONDS: float = 120.0

    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    def get_database_url(self) -> str:
        return self.SQLALCHEMY_DATABASE_URI

    @computed_field
    @property
    def AUDIO_UPLOAD_PATH(self) -> Path:
        """Chemin absolu du dossier des réponses vocales."""
        path = Path(self.AUDIO_UPLOAD_DIR)
        if not path.is_absolute():
            path = Path(__file__).resolve().parents[2] / path
        return path


settings = Settings()
