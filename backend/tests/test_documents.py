import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core.database import get_db
from app.models.user import User
from app.services.auth import auth_service

client = TestClient(app)

def create_test_user(db: Session) -> User:
    user_in = {
        "email": "test@example.com",
        "password": "testpassword",
        "full_name": "Test User"
    }
    return auth_service.register_user(db, user_in)

def get_auth_token(db: Session) -> str:
    user = create_test_user(db)
    return auth_service.create_user_token(user)

def test_upload_cv_success(mock_db_session):
    """Test successful CV upload by authenticated user."""
    token = get_auth_token(mock_db_session)
    
    with open("tests/fixtures/test_cv.pdf", "wb") as f:
        f.write(b"%PDF-1.4 test content")
    
    with open("tests/fixtures/test_cv.pdf", "rb") as f:
        response = client.post(
            "/api/v1/documents/upload/cv",
            files={"file": ("cv.pdf", f, "application/pdf")},
            headers={"Authorization": f"Bearer {token}"}
        )
    
    assert response.status_code == 201
    data = response.json()
    assert data["document_type"] == "cv"
    assert data["original_filename"] == "cv.pdf"

def test_upload_cv_unauthenticated():
    """Test CV upload without authentication."""
    with open("tests/fixtures/test_cv.pdf", "rb") as f:
        response = client.post(
            "/api/v1/documents/upload/cv",
            files={"file": ("cv.pdf", f, "application/pdf")}
        )
    assert response.status_code == 401

def test_upload_cv_invalid_file_type(mock_db_session):
    """Test upload of non-PDF file."""
    token = get_auth_token(mock_db_session)
    
    response = client.post(
        "/api/v1/documents/upload/cv",
        files={"file": ("test.txt", b"test content", "text/plain")},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]

def test_get_my_documents(mock_db_session):
    """Test retrieving user's documents."""
    token = get_auth_token(mock_db_session)
    
    # Upload a document first
    with open("tests/fixtures/test_cv.pdf", "rb") as f:
        client.post(
            "/api/v1/documents/upload/cv",
            files={"file": ("cv.pdf", f, "application/pdf")},
            headers={"Authorization": f"Bearer {token}"}
        )
    
    response = client.get(
        "/api/v1/documents/",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0