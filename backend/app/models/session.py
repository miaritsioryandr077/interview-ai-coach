from datetime import datetime, timezone
from typing import List, Optional

import enum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class SessionStatus(str, enum.Enum):
    """Statut d'une session d'entretien."""

    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Session(Base):
    """Une tentative d'entretien liée à une préparation (Context)."""

    __tablename__ = "interview_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    context_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("contexts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[SessionStatus] = mapped_column(
        Enum(SessionStatus), nullable=False, default=SessionStatus.IN_PROGRESS
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Analyse IA de la session (JSON structuré), nullable.
    analysis: Mapped[Optional[dict]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=True
    )

    # Relations
    context = relationship("Context")
    user = relationship("User")
    responses: Mapped[List["Response"]] = relationship(
        "Response",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="Response.id",
    )
