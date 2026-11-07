"""add_answer_audio_path_to_responses

Revision ID: c3d4e5f6a7b8
Revises: b835e3a01dce
Create Date: 2026-11-07 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, Sequence[str], None] = 'b835e3a01dce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Ajoute la colonne answer_audio_path (chemin du fichier audio) sur responses."""
    op.add_column(
        "responses",
        sa.Column("answer_audio_path", sa.String(length=512), nullable=True),
    )


def downgrade() -> None:
    """Supprime la colonne answer_audio_path."""
    op.drop_column("responses", "answer_audio_path")
