"""Tests des réponses vocales (upload audio + transcription IA).

Couvre : upload valide, validation MIME/taille, isolation cross-user, session
terminée, transcription (succès, échec IA, audio inaudible) et absence de
fichier orphelin en cas d'erreur.
"""
import os
from pathlib import Path
from typing import Dict, Tuple
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.response import Response

from tests.test_sessions import _create_context_with_questions, _register_and_login

FAKE_AUDIO = b"\x1aE\xdf\xa3fake-webm-bytes"


@pytest.fixture()
def audio_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirige les uploads audio vers un dossier temporaire."""
    monkeypatch.setattr(settings, "AUDIO_UPLOAD_DIR", str(tmp_path))
    return tmp_path


def _start_session(client: TestClient, headers: Dict[str, str], suffix: str) -> Tuple[int, int]:
    """Crée un contexte + session, renvoie (session_id, question_id)."""
    me = client.get("/api/v1/users/me", headers=headers)
    user_id = me.json()["id"]
    db = next(client.app.dependency_overrides[get_db]())
    try:
        context_id = _create_context_with_questions(db, user_id, suffix=suffix)
    finally:
        db.close()
    session_id = client.post(
        f"/api/v1/contexts/{context_id}/sessions", headers=headers
    ).json()["id"]
    question_id = client.get(
        f"/api/v1/sessions/{session_id}", headers=headers
    ).json()["questions"][0]["id"]
    return session_id, question_id


def _upload(client: TestClient, headers, session_id, question_id, content=FAKE_AUDIO,
            content_type="audio/webm"):
    return client.post(
        f"/api/v1/sessions/{session_id}/responses/{question_id}/audio",
        headers=headers,
        files={"file": ("answer.webm", content, content_type)},
    )


def test_upload_audio_success(client: TestClient, audio_dir: Path):
    """Un fichier audio valide est stocké et son chemin persisté."""
    _, headers = _register_and_login(client, "audio_ok@example.com")
    session_id, question_id = _start_session(client, headers, "_au1")

    resp = _upload(client, headers, session_id, question_id)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["question_id"] == question_id
    assert data["answer_audio_path"]
    assert Path(data["answer_audio_path"]).exists()
    assert Path(data["answer_audio_path"]).read_bytes() == FAKE_AUDIO
    # Une réponse vocale non transcrite n'a pas encore de texte.
    assert data["text"] == ""


def test_upload_audio_rejects_bad_mime(client: TestClient, audio_dir: Path):
    """Un type MIME non audio est refusé (400) et rien n'est écrit."""
    _, headers = _register_and_login(client, "audio_mime@example.com")
    session_id, question_id = _start_session(client, headers, "_au2")

    resp = _upload(client, headers, session_id, question_id, content_type="application/pdf")
    assert resp.status_code == 400
    assert list(audio_dir.iterdir()) == []


def test_upload_audio_rejects_empty_file(client: TestClient, audio_dir: Path):
    """Un fichier vide est refusé (400)."""
    _, headers = _register_and_login(client, "audio_empty@example.com")
    session_id, question_id = _start_session(client, headers, "_au3")

    resp = _upload(client, headers, session_id, question_id, content=b"")
    assert resp.status_code == 400


def test_upload_audio_rejects_too_large(client: TestClient, audio_dir: Path, monkeypatch):
    """Un fichier dépassant la limite est refusé (413)."""
    monkeypatch.setattr(settings, "MAX_AUDIO_SIZE", 10)
    _, headers = _register_and_login(client, "audio_big@example.com")
    session_id, question_id = _start_session(client, headers, "_au4")

    resp = _upload(client, headers, session_id, question_id, content=b"x" * 50)
    assert resp.status_code == 413
    assert list(audio_dir.iterdir()) == []


def test_upload_audio_replaces_previous_file(client: TestClient, audio_dir: Path):
    """Un nouvel enregistrement remplace l'ancien fichier (pas d'accumulation)."""
    _, headers = _register_and_login(client, "audio_replace@example.com")
    session_id, question_id = _start_session(client, headers, "_au5")

    first = _upload(client, headers, session_id, question_id).json()["answer_audio_path"]
    second = _upload(client, headers, session_id, question_id, content=b"second").json()[
        "answer_audio_path"
    ]
    assert first != second
    assert not Path(first).exists()
    assert Path(second).exists()
    assert len(list(audio_dir.iterdir())) == 1


def test_upload_audio_cross_user(client: TestClient, audio_dir: Path):
    """Impossible d'envoyer un audio sur la session d'un autre utilisateur."""
    owner_id, owner_headers = _register_and_login(client, "audio_owner@example.com")
    _, intruder_headers = _register_and_login(client, "audio_intruder@example.com")
    session_id, question_id = _start_session(client, owner_headers, "_au6")

    resp = _upload(client, intruder_headers, session_id, question_id)
    assert resp.status_code == 404
    assert list(audio_dir.iterdir()) == []


def test_upload_audio_completed_session(client: TestClient, audio_dir: Path):
    """Impossible d'ajouter un audio à une session terminée."""
    _, headers = _register_and_login(client, "audio_closed@example.com")
    session_id, question_id = _start_session(client, headers, "_au7")
    client.post(f"/api/v1/sessions/{session_id}/complete", headers=headers)

    resp = _upload(client, headers, session_id, question_id)
    assert resp.status_code == 400


def test_upload_audio_requires_auth(client: TestClient, audio_dir: Path):
    """L'upload exige une authentification."""
    resp = client.post(
        "/api/v1/sessions/1/responses/1/audio",
        files={"file": ("a.webm", FAKE_AUDIO, "audio/webm")},
    )
    assert resp.status_code == 401


def test_transcribe_success(client: TestClient, audio_dir: Path):
    """La transcription met à jour le texte de la réponse."""
    _, headers = _register_and_login(client, "trans_ok@example.com")
    session_id, question_id = _start_session(client, headers, "_tr1")
    _upload(client, headers, session_id, question_id)

    with patch(
        "app.services.audio_service.llm_service.transcribe_audio",
        new=AsyncMock(return_value="  Bonjour, je suis candidat.  "),
    ):
        resp = client.post(
            f"/api/v1/sessions/{session_id}/responses/{question_id}/transcribe",
            headers=headers,
        )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["question_id"] == question_id
    assert data["text"] == "Bonjour, je suis candidat."
    assert data["response"]["text"] == "Bonjour, je suis candidat."

    # La réponse transcrite apparaît désormais dans la session.
    detail = client.get(f"/api/v1/sessions/{session_id}", headers=headers).json()
    assert len(detail["responses"]) == 1
    assert detail["responses"][0]["text"] == "Bonjour, je suis candidat."


def test_transcribe_without_audio(client: TestClient, audio_dir: Path):
    """Transcription refusée s'il n'y a aucun audio associé."""
    _, headers = _register_and_login(client, "trans_none@example.com")
    session_id, question_id = _start_session(client, headers, "_tr2")

    resp = client.post(
        f"/api/v1/sessions/{session_id}/responses/{question_id}/transcribe",
        headers=headers,
    )
    assert resp.status_code == 404


def test_transcribe_ai_failure_keeps_previous_text(client: TestClient, audio_dir: Path):
    """Un échec IA renvoie 502 et ne modifie pas le texte existant."""
    _, headers = _register_and_login(client, "trans_fail@example.com")
    session_id, question_id = _start_session(client, headers, "_tr3")
    client.post(
        f"/api/v1/sessions/{session_id}/responses",
        headers=headers,
        json={"question_id": question_id, "text": "Texte saisi à la main."},
    )
    _upload(client, headers, session_id, question_id)

    with patch(
        "app.services.audio_service.llm_service.transcribe_audio",
        new=AsyncMock(side_effect=RuntimeError("boom")),
    ):
        resp = client.post(
            f"/api/v1/sessions/{session_id}/responses/{question_id}/transcribe",
            headers=headers,
        )
    assert resp.status_code == 502

    db = next(client.app.dependency_overrides[get_db]())
    try:
        stored = (
            db.query(Response)
            .filter(Response.session_id == session_id, Response.question_id == question_id)
            .first()
        )
        assert stored.text == "Texte saisi à la main."
    finally:
        db.close()


def test_transcribe_empty_result(client: TestClient, audio_dir: Path):
    """Une transcription vide (audio inaudible) renvoie 502."""
    _, headers = _register_and_login(client, "trans_empty@example.com")
    session_id, question_id = _start_session(client, headers, "_tr4")
    _upload(client, headers, session_id, question_id)

    with patch(
        "app.services.audio_service.llm_service.transcribe_audio",
        new=AsyncMock(return_value="   "),
    ):
        resp = client.post(
            f"/api/v1/sessions/{session_id}/responses/{question_id}/transcribe",
            headers=headers,
        )
    assert resp.status_code == 502


def test_transcribe_cross_user(client: TestClient, audio_dir: Path):
    """Impossible de transcrire l'audio d'un autre utilisateur."""
    _, owner_headers = _register_and_login(client, "trans_owner@example.com")
    _, intruder_headers = _register_and_login(client, "trans_intruder@example.com")
    session_id, question_id = _start_session(client, owner_headers, "_tr5")
    _upload(client, owner_headers, session_id, question_id)

    resp = client.post(
        f"/api/v1/sessions/{session_id}/responses/{question_id}/transcribe",
        headers=intruder_headers,
    )
    assert resp.status_code == 404


def test_transcribe_missing_file_on_disk(client: TestClient, audio_dir: Path):
    """Si le fichier a disparu du disque, la transcription renvoie 404."""
    _, headers = _register_and_login(client, "trans_gone@example.com")
    session_id, question_id = _start_session(client, headers, "_tr6")
    path = _upload(client, headers, session_id, question_id).json()["answer_audio_path"]
    os.remove(path)

    resp = client.post(
        f"/api/v1/sessions/{session_id}/responses/{question_id}/transcribe",
        headers=headers,
    )
    assert resp.status_code == 404
