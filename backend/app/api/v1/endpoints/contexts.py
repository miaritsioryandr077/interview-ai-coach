from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.context import ContextCreate, ContextResponse
from app.schemas.question import QuestionResponse
from app.services.context import context_service
from app.services.question_service import question_service
from app.repositories.context import context_repository

router = APIRouter()

@router.post("/", response_model=ContextResponse, status_code=201)
def create_context(
    context_in: ContextCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new preparation context."""
    return context_service.create_context(db, current_user, context_in)

@router.get("/", response_model=List[ContextResponse])
def get_my_contexts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all contexts for the authenticated user."""
    return context_repository.get_by_user_id(db, current_user.id)

@router.post("/{context_id}/generate-questions", response_model=List[QuestionResponse])
async def generate_questions(
    context_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Vérifier l'appartenance
    context = context_repository.get_by_id_and_user(db, context_id, current_user.id)
    if not context:
        raise HTTPException(status_code=404, detail="Préparation non trouvée")
    
    # Générer
    questions = await question_service.generate_and_save_questions(db, context, current_user)
    return questions

@router.get("/{context_id}/questions", response_model=List[QuestionResponse])
def get_questions(
    context_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    context = context_repository.get_by_id_and_user(db, context_id, current_user.id)
    if not context:
        raise HTTPException(status_code=404, detail="Préparation non trouvée")
    return question_service.get_context_questions(db, context_id)