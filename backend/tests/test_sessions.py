"""Tests de la fonctionnalité Session d'entretien.

Couvre : démarrage de session, contrôle de propriété, récupération des questions
ordonnées, enregistrement des réponses, fin de session et sécurité.

Les tests passent par l'API HTTP (comme test_auth.py) afin de valider réellement
l'authentification et les dépendances FastAPI.
"""
from typing import Dict, Tuple

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.context import Context
from app.models.document import Document, DocumentType
from app.models.question import Question
from app.models.response import Response


def _register_and_login(client: TestClient, email: str) -> Tuple[int, Dict[str, str]]:
    """Crée un utilisateur, se connecte et renvoie (user_id, headers)."""
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "secretpassword123", "full_name": "Test User"},
    )
    assert reg.status_code == 201, reg.text
    user_id = reg.json()["id"]

    login = client.post(
        "/api/v1/auth/login", json={"email": email, "password": "secretpassword123"}
    )
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    return user_id, {"Authorization": f"Bearer {token}"}


def _create_context_with_questions(
    db: Session, user_id: int, n_questions: int = 3, suffix: str = ""
) -> int:
    """Crée un Context (+ CV/offre) et n questions, renvoie le context_id."""
    cv = Document(
        user_id=user_id,
        document_type=DocumentType.CV,
        original_filename=f"cv{suffix}.pdf",
        stored_filename=f"stored_cv{suffix}.pdf",
        file_path=f"/tmp/cv{suffix}.pdf",
        file_size=100,
        mime_type="application/pdf",
        extracted_text="CV text",
    )
    job = Document(
        user_id=user_id,
        document_type=DocumentType.JOB_OFFER,
        original_filename=f"job{suffix}.pdf",
        stored_filename=f"stored_job{suffix}.pdf",
        file_path=f"/tmp/job{suffix}.pdf",
        file_size=100,
        mime_type="application/pdf",
        extracted_text="Job text",
    )
    db.add_all([cv, job])
    db.commit()
    db.refresh(cv)
    db.refresh(job)

    context = Context(user_id=user_id, cv_id=cv.id, job_id=job.id, notes="notes")
    db.add(context)
    db.commit()
    db.refresh(context)

    for i in range(n_questions):
        db.add(
            Question(
                context_id=context.id,
                text=f"Question {i}{suffix}",
                category="general",
                difficulty="medium",
                order_index=i,
                expected_duration_seconds=120,
            )
        )
    db.commit()
    return context.id


def test_start_session_authenticated(client: TestClient):
    """1. Un utilisateur authentifié peut démarrer une session."""
    user_id, headers = _register_and_login(client, "start_ok@example.com")

    db = next(client.app.dependency_overrides[get_db]())
    try:
        context_id = _create_context_with_questions(db, user_id, suffix="_a")
    finally:
        db.close()

    resp = client.post(f"/api/v1/contexts/{context_id}/sessions", headers=headers)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["context_id"] == context_id
    assert data["user_id"] == user_id
    assert data["total_questions"] == 3


def test_start_session_unauthenticated(client: TestClient):
    """2. Un utilisateur non authentifié ne peut pas démarrer de session."""
    resp = client.post("/api/v1/contexts/1/sessions")
    assert resp.status_code == 401


def test_cannot_start_session_on_other_users_context(client: TestClient):
    """3. Impossible de démarrer une session sur le Context d'un autre utilisateur."""
    owner_id, _ = _register_and_login(client, "owner_a@example.com")
    _, intruder_headers = _register_and_login(client, "intruder_a@example.com")

    db = next(client.app.dependency_overrides[get_db]())
    try:
        context_id = _create_context_with_questions(db, owner_id, suffix="_b")
    finally:
        db.close()

    resp = client.post(
        f"/api/v1/contexts/{context_id}/sessions", headers=intruder_headers
    )
    assert resp.status_code == 404


def test_session_created_with_in_progress_status(client: TestClient):
    """4. La session est créée avec le statut in_progress."""
    user_id, headers = _register_and_login(client, "status_ok@example.com")

    db = next(client.app.dependency_overrides[get_db]())
    try:
        context_id = _create_context_with_questions(db, user_id, suffix="_c")
    finally:
        db.close()

    resp = client.post(f"/api/v1/contexts/{context_id}/sessions", headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "in_progress"
    assert data["started_at"] is not None
    assert data["ended_at"] is None


def test_cannot_start_session_without_questions(client: TestClient):
    """Une préparation sans question générée ne peut pas démarrer de session."""
    user_id, headers = _register_and_login(client, "noq@example.com")

    db = next(client.app.dependency_overrides[get_db]())
    try:
        context_id = _create_context_with_questions(db, user_id, n_questions=0, suffix="_d")
    finally:
        db.close()

    resp = client.post(f"/api/v1/contexts/{context_id}/sessions", headers=headers)
    assert resp.status_code == 400
    assert "question" in resp.json()["detail"].lower()


def test_get_session_returns_ordered_questions(client: TestClient):
    """5 & 6. Récupération des questions, dans le bon ordre."""
    user_id, headers = _register_and_login(client, "order@example.com")

    db = next(client.app.dependency_overrides[get_db]())
    try:
        context_id = _create_context_with_questions(db, user_id, n_questions=4, suffix="_e")
    finally:
        db.close()

    started = client.post(f"/api/v1/contexts/{context_id}/sessions", headers=headers)
    session_id = started.json()["id"]

    resp = client.get(f"/api/v1/sessions/{session_id}", headers=headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()

    assert data["total_questions"] == 4
    assert len(data["questions"]) == 4
    indexes = [q["order_index"] for q in data["questions"]]
    assert indexes == sorted(indexes)
    assert indexes == [0, 1, 2, 3]


def test_save_response_success(client: TestClient):
    """7. Une réponse est enregistrée correctement."""
    user_id, headers = _register_and_login(client, "answer@example.com")

    db = next(client.app.dependency_overrides[get_db]())
    try:
        context_id = _create_context_with_questions(db, user_id, suffix="_f")
    finally:
        db.close()

    session_id = client.post(
        f"/api/v1/contexts/{context_id}/sessions", headers=headers
    ).json()["id"]

    session_data = client.get(f"/api/v1/sessions/{session_id}", headers=headers).json()
    question_id = session_data["questions"][0]["id"]

    resp = client.post(
        f"/api/v1/sessions/{session_id}/responses",
        headers=headers,
        json={"question_id": question_id, "text": "Ma réponse détaillée."},
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["question_id"] == question_id
    assert data["session_id"] == session_id
    assert data["text"] == "Ma réponse détaillée."

    # La réponse est bien persistée et renvoyée dans la session.
    reloaded = client.get(f"/api/v1/sessions/{session_id}", headers=headers).json()
    assert len(reloaded["responses"]) == 1
    assert reloaded["responses"][0]["text"] == "Ma réponse détaillée."


def test_cannot_answer_in_completed_session(client: TestClient):
    """8. Impossible de répondre dans une session terminée."""
    user_id, headers = _register_and_login(client, "closed@example.com")

    db = next(client.app.dependency_overrides[get_db]())
    try:
        context_id = _create_context_with_questions(db, user_id, suffix="_g")
    finally:
        db.close()

    session_id = client.post(
        f"/api/v1/contexts/{context_id}/sessions", headers=headers
    ).json()["id"]
    question_id = client.get(
        f"/api/v1/sessions/{session_id}", headers=headers
    ).json()["questions"][0]["id"]

    completed = client.post(f"/api/v1/sessions/{session_id}/complete", headers=headers)
    assert completed.status_code == 200

    resp = client.post(
        f"/api/v1/sessions/{session_id}/responses",
        headers=headers,
        json={"question_id": question_id, "text": "Trop tard."},
    )
    assert resp.status_code == 400


def test_cannot_answer_question_from_other_context(client: TestClient):
    """9. Impossible de répondre à une question d'un autre Context."""
    user_id, headers = _register_and_login(client, "crossctx@example.com")

    db = next(client.app.dependency_overrides[get_db]())
    try:
        context_a = _create_context_with_questions(db, user_id, suffix="_h")
        context_b = _create_context_with_questions(db, user_id, suffix="_i")
    finally:
        db.close()

    session_id = client.post(
        f"/api/v1/contexts/{context_a}/sessions", headers=headers
    ).json()["id"]

    # Question appartenant à l'autre préparation (mais bien au même utilisateur).
    other_questions = client.get(
        f"/api/v1/contexts/{context_b}/questions", headers=headers
    ).json()
    foreign_question_id = other_questions[0]["id"]

    resp = client.post(
        f"/api/v1/sessions/{session_id}/responses",
        headers=headers,
        json={"question_id": foreign_question_id, "text": "Hors sujet."},
    )
    assert resp.status_code == 400

    # Et une question inexistante est rejetée aussi.
    resp404 = client.post(
        f"/api/v1/sessions/{session_id}/responses",
        headers=headers,
        json={"question_id": 999, "text": "Fantôme."},
    )
    assert resp404.status_code == 404


def test_complete_session_success(client: TestClient):
    """10. La session est correctement terminée."""
    user_id, headers = _register_and_login(client, "complete@example.com")

    db = next(client.app.dependency_overrides[get_db]())
    try:
        context_id = _create_context_with_questions(db, user_id, suffix="_j")
    finally:
        db.close()

    session_id = client.post(
        f"/api/v1/contexts/{context_id}/sessions", headers=headers
    ).json()["id"]

    resp = client.post(f"/api/v1/sessions/{session_id}/complete", headers=headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["status"] == "completed"
    assert data["ended_at"] is not None

    # Une seconde tentative de clôture est refusée.
    again = client.post(f"/api/v1/sessions/{session_id}/complete", headers=headers)
    assert again.status_code == 400


def test_cannot_access_other_users_session(client: TestClient):
    """11. Impossible de consulter la session d'un autre utilisateur."""
    owner_id, owner_headers = _register_and_login(client, "owner_b@example.com")
    _, intruder_headers = _register_and_login(client, "intruder_b@example.com")

    db = next(client.app.dependency_overrides[get_db]())
    try:
        context_id = _create_context_with_questions(db, owner_id, suffix="_k")
    finally:
        db.close()

    session_id = client.post(
        f"/api/v1/contexts/{context_id}/sessions", headers=owner_headers
    ).json()["id"]

    # GET interdit
    assert client.get(f"/api/v1/sessions/{session_id}", headers=intruder_headers).status_code == 404
    # POST réponse interdit
    assert client.post(
        f"/api/v1/sessions/{session_id}/responses",
        headers=intruder_headers,
        json={"question_id": 1, "text": "Intrusion"},
    ).status_code == 404
    # POST complete interdit
    assert client.post(
        f"/api/v1/sessions/{session_id}/complete", headers=intruder_headers
    ).status_code == 404

    # Le propriétaire y accède sans problème.
    assert client.get(f"/api/v1/sessions/{session_id}", headers=owner_headers).status_code == 200


def test_session_endpoints_require_auth(client: TestClient):
    """Les endpoints sessions exigent une authentification."""
    assert client.get("/api/v1/sessions/1").status_code == 401
    assert client.post("/api/v1/sessions/1/complete").status_code == 401
    assert client.post(
        "/api/v1/sessions/1/responses", json={"question_id": 1, "text": "x"}
    ).status_code == 401


def test_empty_response_treated_as_unanswered(client: TestClient):
    """12. Une réponse vide/espaces est traitée comme non répondue (comptage)."""
    user_id, headers = _register_and_login(client, "emptyresp@example.com")

    db = next(client.app.dependency_overrides[get_db]())
    try:
        context_id = _create_context_with_questions(db, user_id, suffix="_l")
    finally:
        db.close()

    session_id = client.post(
        f"/api/v1/contexts/{context_id}/sessions", headers=headers
    ).json()["id"]
    question_id = client.get(
        f"/api/v1/sessions/{session_id}", headers=headers
    ).json()["questions"][0]["id"]

    # Réponse normale : doit être comptée.
    ok = client.post(
        f"/api/v1/sessions/{session_id}/responses",
        headers=headers,
        json={"question_id": question_id, "text": "Ma réponse."},
    )
    assert ok.status_code == 201

    # Insertion directe d'une réponse vide (contournement de la validation API)
    # pour vérifier la règle de comptage côté backend.
    db = next(client.app.dependency_overrides[get_db]())
    try:
        q2 = db.query(Question).filter(Question.context_id == context_id).all()[1]
        db.add(Response(session_id=session_id, question_id=q2.id, text="   "))
        db.commit()
    finally:
        db.close()

    detail = client.get(f"/api/v1/sessions/{session_id}", headers=headers).json()
    # Seule la réponse non vide est conservée/comptée.
    assert len(detail["responses"]) == 1
    assert detail["responses"][0]["text"] == "Ma réponse."

    # Via l'historique : même règle de comptage.
    history = client.get("/api/v1/sessions/", headers=headers).json()
    sess = next(s for s in history if s["id"] == session_id)
    assert len(sess["responses"]) == 1


def test_failed_save_keeps_session_in_progress(client: TestClient):
    """13. Un échec de sauvegarde ne marque pas la session terminée."""
    user_id, headers = _register_and_login(client, "failsave@example.com")

    db = next(client.app.dependency_overrides[get_db]())
    try:
        context_id = _create_context_with_questions(db, user_id, suffix="_m")
    finally:
        db.close()

    session_id = client.post(
        f"/api/v1/contexts/{context_id}/sessions", headers=headers
    ).json()["id"]
    question_id = client.get(
        f"/api/v1/sessions/{session_id}", headers=headers
    ).json()["questions"][0]["id"]

    # Tentative de sauvegarde avec texte vide -> refusée.
    bad = client.post(
        f"/api/v1/sessions/{session_id}/responses",
        headers=headers,
        json={"question_id": question_id, "text": "   "},
    )
    assert bad.status_code == 422

    # La session reste en cours.
    detail = client.get(f"/api/v1/sessions/{session_id}", headers=headers).json()
    assert detail["status"] == "in_progress"
    assert detail["ended_at"] is None

    # On peut ensuite sauvegarder correctement puis terminer.
    good = client.post(
        f"/api/v1/sessions/{session_id}/responses",
        headers=headers,
        json={"question_id": question_id, "text": "OK"},
    )
    assert good.status_code == 201
    done = client.post(f"/api/v1/sessions/{session_id}/complete", headers=headers)
    assert done.status_code == 200
    assert done.json()["status"] == "completed"

import asyncio
from unittest.mock import AsyncMock, patch


def _valid_analysis_dict() -> dict:
    return {
        "overall_score": 7.5,
        "criteria": {
            "pertinence": 8.0,
            "structure": 7.0,
            "clarte": 7.5,
            "vocabulaire": 7.5,
        },
        "strengths": ["Clarté"],
        "weaknesses": ["Manque d'exemple"],
        "advice": ["Ajouter un exemple concret"],
        "responses": [],
    }


def test_analyze_requires_completed(client: TestClient):
    """Analyse refusée si la session n'est pas terminée."""
    user_id, headers = _register_and_login(client, "an_inprogress@example.com")
    db = next(client.app.dependency_overrides[get_db]())
    try:
        context_id = _create_context_with_questions(db, user_id, suffix="_a1")
    finally:
        db.close()
    session_id = client.post(
        f"/api/v1/contexts/{context_id}/sessions", headers=headers
    ).json()["id"]
    resp = client.post(f"/api/v1/sessions/{session_id}/analyze", headers=headers)
    assert resp.status_code == 400


def test_analyze_no_responses(client: TestClient):
    """Analyse refusée si aucune réponse non vide."""
    user_id, headers = _register_and_login(client, "an_empty@example.com")
    db = next(client.app.dependency_overrides[get_db]())
    try:
        context_id = _create_context_with_questions(db, user_id, suffix="_a2")
    finally:
        db.close()
    session_id = client.post(
        f"/api/v1/contexts/{context_id}/sessions", headers=headers
    ).json()["id"]
    client.post(f"/api/v1/sessions/{session_id}/complete", headers=headers)
    resp = client.post(f"/api/v1/sessions/{session_id}/analyze", headers=headers)
    assert resp.status_code == 400


def test_analyze_success_and_rerun_version(client: TestClient):
    """Analyse persistée + relance incrémente la version."""
    user_id, headers = _register_and_login(client, "an_ok@example.com")
    db = next(client.app.dependency_overrides[get_db]())
    try:
        context_id = _create_context_with_questions(db, user_id, suffix="_a3")
    finally:
        db.close()
    session_id = client.post(
        f"/api/v1/contexts/{context_id}/sessions", headers=headers
    ).json()["id"]
    question_id = client.get(
        f"/api/v1/sessions/{session_id}", headers=headers
    ).json()["questions"][0]["id"]
    client.post(
        f"/api/v1/sessions/{session_id}/responses",
        headers=headers,
        json={"question_id": question_id, "text": "Ma réponse."},
    )
    with patch(
        "app.services.interview_service.llm_service.analyze_interview",
        new=AsyncMock(return_value=_valid_analysis_dict()),
    ):
        client.post(f"/api/v1/sessions/{session_id}/complete", headers=headers)

        r1 = client.post(f"/api/v1/sessions/{session_id}/analyze", headers=headers)
        assert r1.status_code == 200, r1.text
        assert r1.json()["version"] == 2

        r2 = client.post(f"/api/v1/sessions/{session_id}/analyze", headers=headers)
        assert r2.status_code == 200, r2.text
        assert r2.json()["version"] == 3

    g = client.get(f"/api/v1/sessions/{session_id}/analysis", headers=headers)
    assert g.status_code == 200
    assert g.json()["version"] == 3


def test_analyze_cross_user(client: TestClient):
    """Isolation cross-user."""
    owner_id, owner_headers = _register_and_login(client, "an_owner@example.com")
    _, intruder_headers = _register_and_login(client, "an_intruder@example.com")
    db = next(client.app.dependency_overrides[get_db]())
    try:
        context_id = _create_context_with_questions(db, owner_id, suffix="_a4")
    finally:
        db.close()
    session_id = client.post(
        f"/api/v1/contexts/{context_id}/sessions", headers=owner_headers
    ).json()["id"]
    qid = client.get(
        f"/api/v1/sessions/{session_id}", headers=owner_headers
    ).json()["questions"][0]["id"]
    client.post(
        f"/api/v1/sessions/{session_id}/responses",
        headers=owner_headers,
        json={"question_id": qid, "text": "Réponse"},
    )
    client.post(f"/api/v1/sessions/{session_id}/complete", headers=owner_headers)

    assert client.post(
        f"/api/v1/sessions/{session_id}/analyze", headers=intruder_headers
    ).status_code in (403, 404)
    assert client.get(
        f"/api/v1/sessions/{session_id}/analysis", headers=intruder_headers
    ).status_code in (403, 404)


def test_analyze_gemini_failure(client: TestClient):
    """Échec Gemini : session reste terminée, analysis=null, 502."""
    user_id, headers = _register_and_login(client, "an_fail@example.com")
    db = next(client.app.dependency_overrides[get_db]())
    try:
        context_id = _create_context_with_questions(db, user_id, suffix="_a5")
    finally:
        db.close()
    session_id = client.post(
        f"/api/v1/contexts/{context_id}/sessions", headers=headers
    ).json()["id"]
    qid = client.get(
        f"/api/v1/sessions/{session_id}", headers=headers
    ).json()["questions"][0]["id"]
    client.post(
        f"/api/v1/sessions/{session_id}/responses",
        headers=headers,
        json={"question_id": qid, "text": "Réponse"},
    )
    with patch(
        "app.services.interview_service.llm_service.analyze_interview",
        new=AsyncMock(side_effect=RuntimeError("boom")),
    ):
        client.post(f"/api/v1/sessions/{session_id}/complete", headers=headers)

        resp = client.post(f"/api/v1/sessions/{session_id}/analyze", headers=headers)
        assert resp.status_code == 502

    detail = client.get(f"/api/v1/sessions/{session_id}", headers=headers).json()
    assert detail["status"] == "completed"
    assert detail.get("analysis") is None


def test_analyze_invalid_json(client: TestClient):
    """JSON invalide renvoyé par Gemini : non persisté, 502."""
    user_id, headers = _register_and_login(client, "an_invalid@example.com")
    db = next(client.app.dependency_overrides[get_db]())
    try:
        context_id = _create_context_with_questions(db, user_id, suffix="_a6")
    finally:
        db.close()
    session_id = client.post(
        f"/api/v1/contexts/{context_id}/sessions", headers=headers
    ).json()["id"]
    qid = client.get(
        f"/api/v1/sessions/{session_id}", headers=headers
    ).json()["questions"][0]["id"]
    client.post(
        f"/api/v1/sessions/{session_id}/responses",
        headers=headers,
        json={"question_id": qid, "text": "Réponse"},
    )
    with patch(
        "app.services.interview_service.llm_service.analyze_interview",
        new=AsyncMock(return_value={"bad": "data"}),
    ):
        client.post(f"/api/v1/sessions/{session_id}/complete", headers=headers)

        resp = client.post(f"/api/v1/sessions/{session_id}/analyze", headers=headers)
        assert resp.status_code == 502

    detail = client.get(f"/api/v1/sessions/{session_id}", headers=headers).json()
    assert detail.get("analysis") is None
