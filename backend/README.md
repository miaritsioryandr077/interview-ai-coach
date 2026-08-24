# InterviewAI Coach - Backend

FastAPI backend initial setup structured with Clean Architecture principles.

## Structure Architecture

- `app/api/`: Couche API (Endpoints & Routers)
- `app/core/`: Configuration globale, variables d'environnement, session DB
- `app/db/`: Base ORM SQLAlchemy et migrations
- `app/models/`: Modèles ORM SQLAlchemy (Entités de base de données)
- `app/schemas/`: Schémas Pydantic (DTOs / Sérialiseurs)
- `app/repositories/`: Couche d'accès aux données (CRUD / Persistence)
- `app/services/`: Logique métier / cas d'utilisation
- `app/main.py`: Point d'entrée principal de l'application FastAPI

## Lancement rapide

1. **Créer et activer un environnement virtuel** :
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

2. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurer les variables d'environnement** :
   Copier `.env.example` vers `.env` et ajuster la configuration PostgreSQL.

4. **Lancer le serveur de développement** :
   ```bash
   uvicorn app.main:app --reload
   ```

La documentation Swagger UI sera accessible sur `http://localhost:8000/docs`.
