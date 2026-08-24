from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient) -> None:
    """
    Test the root endpoint GET /
    """
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


def test_top_level_health_endpoint(client: TestClient) -> None:
    """
    Test top-level health endpoint GET /health
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_api_v1_health_endpoint(client: TestClient) -> None:
    """
    Test API v1 health endpoint GET /api/v1/health
    """
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
