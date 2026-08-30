from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.context import Context
from app.schemas.context import ContextCreateDB

class ContextRepository:
    def create(self, db: Session, context_in: ContextCreateDB) -> Context:
        db_context = Context(
            user_id=context_in.user_id,
            cv_id=context_in.cv_id,
            job_id=context_in.job_id,
            notes=context_in.notes
        )
        db.add(db_context)
        db.commit()
        db.refresh(db_context)
        return db_context

    def get_by_user_id(self, db: Session, user_id: int) -> List[Context]:
        return db.query(Context).options(
            joinedload(Context.cv),
            joinedload(Context.job)
        ).filter(Context.user_id == user_id).order_by(Context.created_at.desc()).all()

    def get_by_id_and_user(self, db: Session, context_id: int, user_id: int) -> Optional[Context]:
        return db.query(Context).options(
            joinedload(Context.cv),
            joinedload(Context.job)
        ).filter(Context.id == context_id, Context.user_id == user_id).first()

context_repository = ContextRepository()