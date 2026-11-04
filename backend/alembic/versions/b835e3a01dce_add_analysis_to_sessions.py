"""add_analysis_to_sessions

Revision ID: b835e3a01dce
Revises: b1f2a3c4d5e6
Create Date: 2026-10-31 22:24:40.941457

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b835e3a01dce'
down_revision: Union[str, Sequence[str], None] = 'b1f2a3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Ajoute la colonne analysis (JSON/JSONB) sur interview_sessions."""
    bind = op.get_bind()
    dialect = bind.dialect.name
    column_type = (
        sa.dialects.postgresql.JSONB() if dialect == "postgresql" else sa.JSON()
    )
    op.add_column(
        "interview_sessions",
        sa.Column("analysis", column_type, nullable=True),
    )


def downgrade() -> None:
    """Supprime la colonne analysis."""
    op.drop_column("interview_sessions", "analysis")
