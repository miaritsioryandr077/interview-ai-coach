from typing import List, Optional

from sqlalchemy.orm import Session as DBSession

from app.models.response import Response


class ResponseRepository:
    def create(
        self, db: DBSession, session_id: int, question_id: int, text: str
    ) -> Response:
        db_response = Response(
            session_id=session_id,
            question_id=question_id,
            text=text,
        )
        db.add(db_response)
        db.commit()
        db.refresh(db_response)
        return db_response

    def get_by_session_and_question(
        self, db: DBSession, session_id: int, question_id: int
    ) -> Optional[Response]:
        return (
            db.query(Response)
            .filter(Response.session_id == session_id, Response.question_id == question_id)
            .first()
        )

    def get_by_session_id(self, db: DBSession, session_id: int) -> List[Response]:
        return (
            db.query(Response)
            .filter(Response.session_id == session_id)
            .order_by(Response.id.asc())
            .all()
        )

    def update(self, db: DBSession, db_response: Response, text: str) -> Response:
        db_response.text = text
        db.add(db_response)
        db.commit()
        db.refresh(db_response)
        return db_response

    def set_audio_path(
        self, db: DBSession, db_response: Response, audio_path: str
    ) -> Response:
        """Associe (ou remplace) le fichier audio d'une réponse."""
        db_response.answer_audio_path = audio_path
        db.add(db_response)
        db.commit()
        db.refresh(db_response)
        return db_response


response_repository = ResponseRepository()
