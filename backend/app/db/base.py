from typing import Any
from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.
    Automatically generates __tablename__ from class name in lowercase.
    """
    id: Any

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


# Import all models here so Alembic & SQLAlchemy register them
from app.models.user import User  # noqa: F401
