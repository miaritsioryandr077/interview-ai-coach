from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.context import ContextCreate, ContextCreateDB
from app.repositories.context import context_repository
from app.repositories.document import document_repository
from app.models.user import User

class ContextService:
    def create_context(self, db: Session, user: User, context_in: ContextCreate):
        # Sécurité : Vérifier que le CV appartient à l'utilisateur
        cv = document_repository.get_by_id_and_user(db, context_in.cv_id, user.id)
        if not cv or cv.document_type.value != "cv":
            raise HTTPException(status_code=400, detail="CV invalide ou non autorisé.")

        # Sécurité : Vérifier que l'offre appartient à l'utilisateur
        job = document_repository.get_by_id_and_user(db, context_in.job_id, user.id)
        if not job or job.document_type.value != "job_offer":
            raise HTTPException(status_code=400, detail="Offre d'emploi invalide ou non autorisée.")

        db_in = ContextCreateDB(
            user_id=user.id,
            cv_id=context_in.cv_id,
            job_id=context_in.job_id,
            notes=context_in.notes
        )
        return context_repository.create(db, db_in)

context_service = ContextService()