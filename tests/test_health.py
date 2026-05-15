def test_health_endpoint_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_endpoint_returns_expected_payload(client):
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert "status" in data
    assert data["status"] == "healthy"

    assert "redis" in data
    assert data["redis"] in ["healthy", "unhealthy"]
