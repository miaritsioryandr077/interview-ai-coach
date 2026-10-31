from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.models.context import Context
from app.models.question import Question
from app.models.session import Session, SessionStatus
from app.models.user import User
from app.repositories.context import context_repository
from app.repositories.question import question_repository
from app.repositories.response import response_repository
from app.repositories.session import session_repository
from app.schemas.session import SessionResponse


class InterviewService:
    """Logique métier des sessions d'entretien (démarrage, réponses, fin)."""

    def _build_session_response(
        self, db: DBSession, db_session: Session
    ) -> SessionResponse:
        """Construit la réponse API : session + questions ordonnées + réponses."""
        questions = question_repository.get_by_context_id(db, db_session.context_id)
        responses = response_repository.get_by_session_id(db, db_session.id)

        payload = SessionResponse.model_validate(db_session)
        payload.total_questions = len(questions)
        payload.questions = questions
        payload.responses = responses
        return payload

    def start_session(self, db: DBSession, user: User, context_id: int) -> SessionResponse:
        """Démarre une session à partir d'un Context appartenant à l'utilisateur."""
        context: Context | None = context_repository.get_by_id_and_user(
            db, context_id, user.id
        )
        if not context:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Préparation non trouvée",
            )

        # La session ne génère AUCUNE question : elle réutilise celles existantes.
        questions = question_repository.get_by_context_id(db, context_id)
        if not questions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Aucune question générée pour cette préparation.",
            )

        db_session = session_repository.create(db, context_id=context.id, user_id=user.id)
        return self._build_session_response(db, db_session)

    def get_session(self, db: DBSession, user: User, session_id: int) -> SessionResponse:
        """Retourne une session de l'utilisateur avec ses questions ordonnées."""
        db_session = session_repository.get_by_id_and_user(db, session_id, user.id)
        if not db_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session non trouvée",
            )
        return self._build_session_response(db, db_session)

    def get_my_sessions(self, db: DBSession, user: User):
        sessions = session_repository.get_by_user_id(db, user.id)
        result = []
        for db_session in sessions:
            questions = question_repository.get_by_context_id(db, db_session.context_id)
            responses = response_repository.get_by_session_id(db, db_session.id)
            payload = SessionResponse.model_validate(db_session)
            payload.total_questions = len(questions)
            payload.questions = []
            payload.responses = responses
            result.append(payload)
        return result

    def save_response(
        self, db: DBSession, user: User, session_id: int, question_id: int, text: str
    ):
        """Enregistre (ou remplace) la réponse à une question d'une session en cours."""
        db_session = session_repository.get_by_id_and_user(db, session_id, user.id)
        if not db_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session non trouvée",
            )

        if db_session.status != SessionStatus.IN_PROGRESS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cette session est terminée, impossible d'y répondre.",
            )

        # On ne fait JAMAIS confiance au question_id du frontend : on recharge la
        # question depuis la base et on vérifie qu'elle appartient bien au Context
        # de la session.
        question: Question | None = (
            db.query(Question).filter(Question.id == question_id).first()
        )
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question non trouvée",
            )
        if question.context_id != db_session.context_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cette question n'appartient pas à la préparation de la session.",
            )

        if not text or not text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le texte de la réponse ne peut pas être vide.",
            )

        existing = response_repository.get_by_session_and_question(
            db, session_id, question_id
        )
        if existing:
            return response_repository.update(db, existing, text)
        return response_repository.create(db, session_id, question_id, text)

    def complete_session(self, db: DBSession, user: User, session_id: int) -> SessionResponse:
        """Termine une session en cours."""
        db_session = session_repository.get_by_id_and_user(db, session_id, user.id)
        if not db_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session non trouvée",
            )

        if db_session.status != SessionStatus.IN_PROGRESS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cette session est déjà terminée.",
            )

        db_session.status = SessionStatus.COMPLETED
        db_session.ended_at = datetime.now(timezone.utc)
        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        return self._build_session_response(db, db_session)


interview_service = InterviewService()
