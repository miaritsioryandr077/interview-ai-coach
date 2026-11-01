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
from app.schemas.analysis import AnalysisResponse
from app.schemas.session import SessionResponse
from app.services.llm_service import llm_service


class InterviewService:
    """Logique métier des sessions d'entretien (démarrage, réponses, fin)."""

    def _build_session_response(
        self, db: DBSession, db_session: Session
    ) -> SessionResponse:
        """Construit la réponse API : session + questions ordonnées + réponses."""
        questions = question_repository.get_by_context_id(db, db_session.context_id)
        raw_responses = response_repository.get_by_session_id(db, db_session.id)
        # Une réponse vide (ou ne contenant que des espaces) est traitée
        # comme non répondue, côté comptage et affichage.
        responses = [r for r in raw_responses if r.text and r.text.strip()]

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
            raw_responses = response_repository.get_by_session_id(db, db_session.id)
            responses = [r for r in raw_responses if r.text and r.text.strip()]
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

    def analyze_session(self, db: DBSession, user: User, session_id: int) -> AnalysisResponse:
        """Analyse une session terminée (idempotent, version++)."""
        db_session = session_repository.get_by_id_and_user(db, session_id, user.id)
        if not db_session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session non trouvée")
        if db_session.status != SessionStatus.COMPLETED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La session doit être terminée pour être analysée.")

        questions = question_repository.get_by_context_id(db, db_session.context_id)
        responses = response_repository.get_by_session_id(db, db_session.id)
        resp_map = {r.question_id: r for r in responses if r.text and r.text.strip()}

        qa_list = []
        for q in questions:
            r = resp_map.get(q.id)
            qa_list.append({
                "question_id": q.id,
                "question": q.text,
                "answer": r.text if r else None,
            })

        non_empty = [item for item in qa_list if item["answer"]]
        if not non_empty:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Aucune réponse à analyser")

        import asyncio
        try:
            raw = asyncio.run(llm_service.analyze_interview(qa_list))
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Analyse IA indisponible : {e}")

        from datetime import datetime, timezone
        try:
            resp_by_id = {r["question_id"]: r for r in raw.get("responses", [])}
            normalized_responses = []
            for item in qa_list:
                qid = item["question_id"]
                r = resp_by_id.get(qid, {})
                answered = bool(item["answer"])
                if not answered:
                    normalized_responses.append({
                        "question_id": qid,
                        "question": item["question"],
                        "answered": False,
                        "score": None,
                        "feedback": None,
                        "improved_answer": None,
                    })
                else:
                    normalized_responses.append({
                        "question_id": qid,
                        "question": item["question"],
                        "answered": True,
                        "score": r.get("score"),
                        "feedback": r.get("feedback"),
                        "improved_answer": r.get("improved_answer"),
                    })
            raw["responses"] = normalized_responses

            prev = db_session.analysis if isinstance(db_session.analysis, dict) else {}
            version = (prev.get("version", 0) if isinstance(prev, dict) else 0) + 1
            raw["version"] = version
            raw["model"] = getattr(llm_service, "model", "gemini")
            raw["generated_at"] = datetime.now(timezone.utc).isoformat()

            analysis = AnalysisResponse.model_validate(raw)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Analyse IA invalide : {e}")

        db_session.analysis = analysis.model_dump(mode="json")
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return analysis


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

        # Analyse IA best-effort : ne bloque jamais la clôture.
        non_empty = [
            r for r in response_repository.get_by_session_id(db, db_session.id)
            if r.text and r.text.strip()
        ]
        if non_empty:
            try:
                self.analyze_session(db, user, db_session.id)
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(
                    "Analyse IA échouée pour la session %s : %s", db_session.id, e
                )

        return self._build_session_response(db, db_session)


interview_service = InterviewService()
