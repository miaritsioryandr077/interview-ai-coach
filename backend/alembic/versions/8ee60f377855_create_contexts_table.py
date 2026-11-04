"""create_contexts_table

Revision ID: 8ee60f377855
Revises: e14bfd7e608e
Create Date: 2026-08-30 13:41:10.315867

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ee60f377855'
down_revision: Union[str, Sequence[str], None] = 'e14bfd7e608e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Crée la table ``contexts`` (importation laissée vide par autogenerate)."""
    op.create_table(
        "contexts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("cv_id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["cv_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_contexts_id"), "contexts", ["id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_contexts_id"), table_name="contexts")
    op.drop_table("contexts")
