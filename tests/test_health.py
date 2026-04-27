from fastapi.testclient import TestClient
from todo_service.app.main import app

client = TestClient(app)


def test_health_endpoint_returns_200():
    response = client.get("/health")
    assert response.status_code == 200


def test_health_endpoint_returns_expected_payload():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert "status" in data
    assert data["status"] == "healthy"

    assert "redis" in data
    assert data["redis"] in ["healthy", "unhealthy"]