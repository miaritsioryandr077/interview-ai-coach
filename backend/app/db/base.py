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


# NE PAS importer les modèles ici !
# Les modèles seront importés dans app/models/__init__.py