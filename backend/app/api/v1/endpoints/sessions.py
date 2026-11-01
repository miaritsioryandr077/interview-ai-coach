from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.repositories.session import session_repository
from app.schemas.analysis import AnalysisResponse
from app.schemas.response import ResponseCreate
from app.schemas.response import ResponseResponse as ResponseSchema
from app.schemas.session import SessionResponse
from app.services.interview_service import interview_service

router = APIRouter()


@router.get("/", response_model=List[SessionResponse])
def get_my_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Liste les sessions d'entretien de l'utilisateur authentifié."""
    return interview_service.get_my_sessions(db, current_user)


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retourne une session (questions ordonnées + réponses) de l'utilisateur."""
    return interview_service.get_session(db, current_user, session_id)


@router.post("/{session_id}/responses", response_model=ResponseSchema, status_code=201)
def save_response(
    session_id: int,
    payload: ResponseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Enregistre la réponse à une question d'une session en cours."""
    return interview_service.save_response(
        db, current_user, session_id, payload.question_id, payload.text
    )


@router.post("/{session_id}/analyze", response_model=AnalysisResponse)
def analyze_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Analyse IA d'une session terminée."""
    return interview_service.analyze_session(db, current_user, session_id)


@router.get("/{session_id}/analysis", response_model=Optional[AnalysisResponse])
def get_analysis(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Renvoie l'analyse existante (ou null)."""
    db_session = session_repository.get_by_id_and_user(db, session_id, current_user.id)
    if not db_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session non trouvée")
    if db_session.analysis is None:
        return None
    return AnalysisResponse.model_validate(db_session.analysis)
@router.post("/{session_id}/complete", response_model=SessionResponse)
def complete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Termine une session d'entretien en cours."""
    return interview_service.complete_session(db, current_user, session_id)
