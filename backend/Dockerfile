FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Dépendances système pour psycopg2 (libpq) et compilation éventuelle.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt "psycopg[binary]>=3.1"

COPY . .

EXPOSE 8000

# alembic/env.py lit uniquement sqlalchemy.url de alembic.ini (pas DATABASE_URL) :
# on le surcharge au démarrage. Le driver est forcé à psycopg2 (psycopg2-binary)
# car SQLAlchemy 2.1 choisirait sinon le dialecte "psycopg" (psycopg3).
# set -e : si la migration échoue, le conteneur ne démarre pas.
CMD ["sh", "-c", "set -e; if [ -n \"$DATABASE_URL\" ]; then url=$(echo \"$DATABASE_URL\" | sed 's#^postgresql://#postgresql+psycopg2://#'); sed -i \"s|^sqlalchemy.url = .*|sqlalchemy.url = $url|\" alembic.ini; fi; alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]
