"""create_sessions_and_responses_tables

Revision ID: b1f2a3c4d5e6
Revises: 7af465c8649c
Create Date: 2026-01-01 00:00:00.000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1f2a3c4d5e6'
down_revision: Union[str, Sequence[str], None] = '7af465c8649c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Crée les tables des sessions d'entretien et des réponses."""
    op.create_table(
        "interview_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("context_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["context_id"], ["contexts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_interview_sessions_id"), "interview_sessions", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_interview_sessions_context_id"),
        "interview_sessions",
        ["context_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_interview_sessions_user_id"),
        "interview_sessions",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "responses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["session_id"], ["interview_sessions.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_responses_id"), "responses", ["id"], unique=False)
    op.create_index(
        op.f("ix_responses_session_id"), "responses", ["session_id"], unique=False
    )
    op.create_index(
        op.f("ix_responses_question_id"), "responses", ["question_id"], unique=False
    )


def downgrade() -> None:
    """Supprime les tables des sessions d'entretien et des réponses."""
    op.drop_index(op.f("ix_responses_question_id"), table_name="responses")
    op.drop_index(op.f("ix_responses_session_id"), table_name="responses")
    op.drop_index(op.f("ix_responses_id"), table_name="responses")
    op.drop_table("responses")

    op.drop_index(op.f("ix_interview_sessions_user_id"), table_name="interview_sessions")
    op.drop_index(
        op.f("ix_interview_sessions_context_id"), table_name="interview_sessions"
    )
    op.drop_index(op.f("ix_interview_sessions_id"), table_name="interview_sessions")
    op.drop_table("interview_sessions")
