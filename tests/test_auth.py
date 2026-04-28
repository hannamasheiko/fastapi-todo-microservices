import uuid


def create_test_user(client):
    """Створити унікального тестового користувача через API"""
    unique_suffix = uuid.uuid4().hex[:8]

    user_data = {
        "username": f"testuser_{unique_suffix}",
        "email": f"test_{unique_suffix}@example.com",
        "password": "TestPassword123!"
    }

    response = client.post("/api/v1/auth/register", json=user_data)

    assert response.status_code == 201

    return user_data


def test_login_success(client):
    user = create_test_user(client)

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": user["username"],
            "password": user["password"]
        }
    )

    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password_returns_401(client):
    user = create_test_user(client)

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": user["username"],
            "password": "wrong_password"
        }
    )

    assert response.status_code == 401

    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Invalid credentials"


def test_get_todos_without_token_is_rejected(client):
    response = client.get("/api/v1/todos")

    assert response.status_code in [401, 403]

    data = response.json()
    assert "detail" in data


def test_get_todos_with_valid_token_returns_200(client):
    user = create_test_user(client)

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": user["username"],
            "password": user["password"]
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/todos",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

def test_get_me_with_valid_token_returns_current_user(client):
    user = create_test_user(client)

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": user["username"],
            "password": user["password"]
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    data = response.json()
    assert data["username"] == user["username"]
    assert data["email"] == user["email"]
    assert data["is_active"] is True
    assert "id" in data


def test_get_me_with_invalid_token_is_rejected(client):
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )

    assert response.status_code in [401, 403]

    data = response.json()
    assert "detail" in data