from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.repositories.user import user_repository
from app.schemas.user import UserProfileResponse, UserProfileUpdate

router = APIRouter()


@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Get current user profile",
)
def get_my_profile(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Return the authenticated user's profile. Identity comes from the JWT only.
    """
    return current_user


@router.put(
    "/me",
    response_model=UserProfileResponse,
    summary="Update current user profile",
)
def update_my_profile(
    profile_in: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update the authenticated user's profile. There is no user id in the path,
    so a caller cannot target another account.
    """
    return user_repository.update_profile(db=db, user=current_user, profile_in=profile_in)
