from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.context import ContextCreate, ContextResponse
from app.services.context import context_service
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