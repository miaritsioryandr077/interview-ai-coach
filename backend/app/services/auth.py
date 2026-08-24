from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.user import UserCreate
from app.repositories.user import user_repository
from app.core.security import verify_password, create_access_token


class AuthService:
    def register_user(self, db: Session, user_in: UserCreate) -> User:
        """
        Register a new user after verifying email uniqueness.
        """
        existing_user = user_repository.get_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists.",
            )
        return user_repository.create(db, user_in=user_in)

    def authenticate_user(
        self, db: Session, email: str, password: str
    ) -> Optional[User]:
        """
        Authenticate user credentials. Returns User if valid, None otherwise.
        """
        user = user_repository.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def create_user_token(self, user: User) -> str:
        """
        Generate JWT access token for user.
        """
        return create_access_token(subject=user.id)


auth_service = AuthService()
