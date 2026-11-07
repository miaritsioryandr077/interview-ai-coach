"""Service des réponses vocales : upload du fichier audio et transcription IA.

Le binaire audio n'est jamais stocké en base : seule son chemin
(`responses.answer_audio_path`) est persisté.
"""
import logging
import os
import uuid
from typing import Optional

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session as DBSession

from app.core.config import settings
from app.models.question import Question
from app.models.response import Response
from app.models.session import Session, SessionStatus
from app.models.user import User
from app.repositories.response import response_repository
from app.repositories.session import session_repository
from app.schemas.response import ResponseResponse, TranscriptionResponse
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

# Extension de fichier associée à chaque type MIME autorisé.
MIME_TO_EXTENSION = {
    "audio/webm": ".webm",
    "audio/wav": ".wav",
    "audio/mpeg": ".mp3",
    "audio/ogg": ".ogg",
}

# Certains navigateurs ajoutent des paramètres (ex: "audio/webm;codecs=opus").
def _normalize_mime(content_type: Optional[str]) -> str:
    return (content_type or "").split(";")[0].strip().lower()


class AudioService:
    """Logique métier des réponses vocales d'une session d'entretien."""

    def _get_owned_session(self, db: DBSession, user: User, session_id: int) -> Session:
        """Session de l'utilisateur courant, sinon 404 (isolation cross-user)."""
        db_session = session_repository.get_by_id_and_user(db, session_id, user.id)
        if not db_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session non trouvée",
            )
        return db_session

    def _ensure_in_progress(self, db_session: Session) -> None:
        if db_session.status != SessionStatus.IN_PROGRESS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cette session est terminée, impossible d'y répondre.",
            )

    def _get_session_question(
        self, db: DBSession, db_session: Session, question_id: int
    ) -> Question:
        """Question appartenant bien au Context de la session."""
        question: Optional[Question] = (
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
        return question

    def _validate_audio(self, file: UploadFile) -> str:
        """Valide le type MIME et la taille (10 Mo max). Renvoie le MIME normalisé."""
        mime = _normalize_mime(file.content_type)
        if mime not in settings.ALLOWED_AUDIO_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Type de fichier audio non supporté. Types autorisés : "
                    + ", ".join(settings.ALLOWED_AUDIO_MIME_TYPES)
                ),
            )

        # Taille : on se positionne en fin de flux pour la mesurer.
        file.file.seek(0, os.SEEK_END)
        size = file.file.tell()
        file.file.seek(0)
        if size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le fichier audio est vide.",
            )
        if size > settings.MAX_AUDIO_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail=(
                    "Fichier audio trop volumineux. Taille maximale : "
                    f"{settings.MAX_AUDIO_SIZE // (1024 * 1024)} Mo."
                ),
            )
        return mime

    def _save_audio_file(
        self, file: UploadFile, session_id: int, question_id: int, mime: str
    ) -> str:
        """Écrit le fichier dans uploads/audio/ et renvoie son chemin."""
        audio_dir = settings.AUDIO_UPLOAD_PATH
        os.makedirs(audio_dir, exist_ok=True)

        extension = MIME_TO_EXTENSION.get(mime, ".webm")
        filename = f"{session_id}_{question_id}_{uuid.uuid4()}{extension}"
        file_path = audio_dir / filename

        with open(file_path, "wb") as buffer:
            while chunk := file.file.read(1024 * 1024):
                buffer.write(chunk)
        file.file.seek(0)
        return str(file_path)

    def _remove_file(self, path: Optional[str]) -> None:
        """Suppression best-effort d'un ancien fichier audio."""
        if not path:
            return
        try:
            if os.path.exists(path):
                os.remove(path)
        except OSError:  # pragma: no cover - nettoyage non bloquant
            logger.warning("Impossible de supprimer l'ancien audio %s", path)

    def upload_audio(
        self,
        db: DBSession,
        user: User,
        session_id: int,
        question_id: int,
        file: UploadFile,
    ) -> ResponseResponse:
        """Enregistre le fichier audio d'une réponse et stocke son chemin."""
        db_session = self._get_owned_session(db, user, session_id)
        self._ensure_in_progress(db_session)
        self._get_session_question(db, db_session, question_id)

        mime = self._validate_audio(file)
        file_path = self._save_audio_file(file, session_id, question_id, mime)

        try:
            existing = response_repository.get_by_session_and_question(
                db, session_id, question_id
            )
            if existing:
                previous_path = existing.answer_audio_path
                db_response = response_repository.set_audio_path(
                    db, existing, file_path
                )
                if previous_path and previous_path != file_path:
                    self._remove_file(previous_path)
            else:
                # Une réponse vocale non encore transcrite n'a pas de texte :
                # elle reste `answered=false` tant que la transcription n'a pas eu lieu.
                db_response = response_repository.create(db, session_id, question_id, "")
                db_response = response_repository.set_audio_path(
                    db, db_response, file_path
                )
        except Exception:
            # Pas de fichier orphelin si la persistance échoue.
            self._remove_file(file_path)
            raise

        return ResponseResponse.model_validate(db_response)

    async def transcribe(
        self, db: DBSession, user: User, session_id: int, question_id: int
    ) -> TranscriptionResponse:
        """Transcrit l'audio associé à une réponse et met à jour son texte."""
        db_session = self._get_owned_session(db, user, session_id)
        self._ensure_in_progress(db_session)
        self._get_session_question(db, db_session, question_id)

        db_response: Optional[Response] = (
            response_repository.get_by_session_and_question(db, session_id, question_id)
        )
        if not db_response or not db_response.answer_audio_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aucun fichier audio associé à cette réponse.",
            )
        if not os.path.exists(db_response.answer_audio_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Le fichier audio associé est introuvable sur le serveur.",
            )

        extension = os.path.splitext(db_response.answer_audio_path)[1].lower()
        mime_type = next(
            (m for m, ext in MIME_TO_EXTENSION.items() if ext == extension),
            "audio/webm",
        )

        # En cas d'échec, le texte existant n'est jamais écrasé : toute erreur
        # du service IA est normalisée en 502.
        try:
            text = await llm_service.transcribe_audio(
                db_response.answer_audio_path, mime_type
            )
        except HTTPException:
            raise
        except Exception as e:  # noqa: BLE001 - normalisation en 502
            logger.error("Transcription échouée : %r", e)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=(
                    "La transcription audio a échoué (service IA indisponible). "
                    "Votre réponse précédente a été conservée, vous pouvez réessayer."
                ),
            )
        text = (text or "").strip()
        if not text:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=(
                    "La transcription n'a produit aucun texte (audio inaudible). "
                    "Votre réponse précédente a été conservée."
                ),
            )

        db_response = response_repository.update(db, db_response, text)
        return TranscriptionResponse(
            question_id=question_id,
            text=text,
            response=ResponseResponse.model_validate(db_response),
        )


audio_service = AudioService()
