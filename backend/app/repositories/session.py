from typing import List, Optional

from sqlalchemy.orm import Session as DBSession, joinedload

from app.models.session import Session, SessionStatus


class SessionRepository:
    def create(self, db: DBSession, context_id: int, user_id: int) -> Session:
        db_session = Session(
            context_id=context_id,
            user_id=user_id,
            status=SessionStatus.IN_PROGRESS,
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return db_session

    def get_by_id(self, db: DBSession, session_id: int) -> Optional[Session]:
        return db.query(Session).options(
            joinedload(Session.context),
            joinedload(Session.responses),
        ).filter(Session.id == session_id).first()

    def get_by_id_and_user(
        self, db: DBSession, session_id: int, user_id: int
    ) -> Optional[Session]:
        """Retourne la session uniquement si elle appartient à l'utilisateur."""
        return db.query(Session).options(
            joinedload(Session.context),
            joinedload(Session.responses),
        ).filter(Session.id == session_id, Session.user_id == user_id).first()

    def get_by_user_id(self, db: DBSession, user_id: int) -> List[Session]:
        return (
            db.query(Session)
            .options(joinedload(Session.context))
            .filter(Session.user_id == user_id)
            .order_by(Session.started_at.desc())
            .all()
        )

    def complete(self, db: DBSession, db_session: Session) -> Session:
        db_session.status = SessionStatus.COMPLETED
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return db_session


session_repository = SessionRepository()
