from datetime import datetime, timezone
from typing import Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.user import User
from app.schemas.user import UserCreate, UserProfileUpdate
from app.core.security import hash_password


def split_full_name(full_name: Optional[str]) -> tuple[Optional[str], Optional[str]]:
    if not full_name or not full_name.strip():
        return None, None
    parts = full_name.strip().split(None, 1)
    first_name = parts[0]
    last_name = parts[1] if len(parts) > 1 else None
    return first_name, last_name


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
        first_name, last_name = split_full_name(user_in.full_name)
        db_user = User(
            email=user_in.email.lower().strip(),
            hashed_password=hash_password(user_in.password),
            full_name=user_in.full_name.strip() if user_in.full_name else None,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
            is_superuser=False,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def update_profile(self, db: Session, user: User, profile_in: UserProfileUpdate) -> User:
        """
        Update the authenticated user's profile fields only (never password).
        """
        updates: dict[str, Any] = profile_in.model_dump(exclude_unset=True)
        for field_name, value in updates.items():
            stored = value.value if hasattr(value, "value") else value
            setattr(user, field_name, stored)

        first = (user.first_name or "").strip()
        last = (user.last_name or "").strip()
        combined = f"{first} {last}".strip()
        if combined:
            user.full_name = combined

        user.updated_at = datetime.now(timezone.utc)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


user_repository = UserRepository()
