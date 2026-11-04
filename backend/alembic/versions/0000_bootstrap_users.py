"""Bootstrap: users table (historiquement créée par create_all, hors Alembic).

Revision ID: 0000_bootstrap_users
Revises:
Create Date: 2026-11-04

Contexte
--------
Jusqu'ici la base locale était créée par ``Base.metadata.create_all`` (au
démarrage de FastAPI), puis ``alembic upgrade head`` était "adopté" avec
``alembic stamp`` (généralement ``stamp b1f2a3c4d5e6``).

Les migrations existantes utilisent ``users.id`` en clé étrangère, mais aucune
ne crée la table ``users``. Pour que ``alembic upgrade head`` fonctionne seul
sur une base vierge (cas Docker), cette révision racine crée ``users`` de façon
idempotente.

Rétro-compatibilité
-------------------
Sur une base déjà stampée ``b1f2a3c4d5e6`` ou ``b835e3a01dce`` (sans cette
révision dans ``alembic_version``), utiliser ``alembic stamp --purge head``
une seule fois : les CREATE ... IF NOT EXISTS sont alors des no-op.

Historique linéaire :
    0000_bootstrap_users -> e14bfd7e608e -> 8ee60f377855 -> 7af465c8649c
    -> b1f2a3c4d5e6 -> b835e3a01dce
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0000_bootstrap_users"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Crée ``users`` si absente, avec toutes les colonnes du modèle User."""
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL NOT NULL,
            email VARCHAR(255) NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            full_name VARCHAR(255),
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            education_level VARCHAR(50),
            field VARCHAR(255),
            objective VARCHAR(50),
            preferred_language VARCHAR(10),
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE,
            PRIMARY KEY (id)
        )
        """
    )
    # ALTER ... IF NOT EXISTS : safe sur une base créée par une ancienne
    # version de create_all (colonnes de profil absentes).
    for column, ddl in (
        ("full_name", "VARCHAR(255)"),
        ("first_name", "VARCHAR(100)"),
        ("last_name", "VARCHAR(100)"),
        ("education_level", "VARCHAR(50)"),
        ("field", "VARCHAR(255)"),
        ("objective", "VARCHAR(50)"),
        ("preferred_language", "VARCHAR(10)"),
        ("updated_at", "TIMESTAMP WITH TIME ZONE"),
    ):
        op.execute(f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {column} {ddl}")
    op.execute(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS "
        "is_superuser BOOLEAN NOT NULL DEFAULT FALSE"
    )
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users (email)")


def downgrade() -> None:
    # On ne supprime volontairement pas la table utilisateurs (données métier).
    pass
