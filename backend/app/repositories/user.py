from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password


class UserRepository:
    def get_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """
        Fetch user by primary key ID.
        """
        return db.scalar(select(User).where(User.id == user_id))

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        Fetch user by email address.
        """
        return db.scalar(select(User).where(User.email == email.lower().strip()))

    def create(self, db: Session, user_in: UserCreate) -> User:
        """
        Create and persist a new user entity.
        """
        db_user = User(
            email=user_in.email.lower().strip(),
            hashed_password=hash_password(user_in.password),
            full_name=user_in.full_name,
            is_active=True,
            is_superuser=False,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user


user_repository = UserRepository()
