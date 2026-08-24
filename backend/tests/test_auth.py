from fastapi.testclient import TestClient


def test_register_user_success(client: TestClient) -> None:
    """
    Test successful user registration.
    """
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "testuser@example.com",
            "password": "secretpassword123",
            "full_name": "Test User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert data["full_name"] == "Test User"
    assert "id" in data
    assert "hashed_password" not in data


def test_register_duplicate_email(client: TestClient) -> None:
    """
    Test registration fails when email is already registered.
    """
    # Second attempt with same email
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "testuser@example.com",
            "password": "anotherpassword",
            "full_name": "Duplicate User",
        },
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_login_success(client: TestClient) -> None:
    """
    Test successful user login returning JWT token.
    """
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "secretpassword123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client: TestClient) -> None:
    """
    Test login fails with incorrect password.
    """
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401


def test_get_me_unauthorized(client: TestClient) -> None:
    """
    Test /auth/me returns 401 when no token is provided.
    """
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_get_me_authorized(client: TestClient) -> None:
    """
    Test /auth/me returns user profile when valid JWT token is sent.
    """
    # Login first
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "secretpassword123",
        },
    )
    token = login_response.json()["access_token"]

    # Request /auth/me with Bearer token
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert data["full_name"] == "Test User"
