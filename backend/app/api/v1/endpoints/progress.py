from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.progress import PreparationProgressResponse, ProgressResponse
from app.services.progress_service import progress_service

router = APIRouter()


@router.get("/progress", response_model=ProgressResponse)
def get_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return progress_service.get_progress(db, current_user)


@router.get("/preparations/{preparation_id}/progress", response_model=PreparationProgressResponse)
def get_preparation_progress(
    preparation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return progress_service.get_preparation_progress(db, current_user, preparation_id)