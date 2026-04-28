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


def get_auth_headers(client, user):
    """Залогінити користувача і повернути Authorization headers"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": user["username"],
            "password": user["password"]
        }
    )

    assert response.status_code == 200

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_todo(client, headers, title="Test todo", description="Test description", completed=False, priority=1):
    """Створити todo через API"""
    response = client.post(
        "/api/v1/todos",
        headers=headers,
        json={
            "title": title,
            "description": description,
            "completed": completed,
            "priority": priority
        }
    )

    return response


def test_get_todos_returns_only_current_user_items(client):
    user1 = create_test_user(client)
    headers1 = get_auth_headers(client, user1)

    user2 = create_test_user(client)
    headers2 = get_auth_headers(client, user2)

    create_todo(client, headers1, title="User1 todo 1")
    create_todo(client, headers1, title="User1 todo 2")
    create_todo(client, headers2, title="User2 todo 1")

    response = client.get("/api/v1/todos", headers=headers1)

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2

    titles = [todo["title"] for todo in data]
    assert "User1 todo 1" in titles
    assert "User1 todo 2" in titles
    assert "User2 todo 1" not in titles


def test_create_todo_with_valid_token_returns_201(client):
    user = create_test_user(client)
    headers = get_auth_headers(client, user)

    response = client.post(
        "/api/v1/todos",
        headers=headers,
        json={
            "title": "Buy milk",
            "description": "2 liters",
            "completed": False,
            "priority": 2
        }
    )

    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "Buy milk"
    assert data["description"] == "2 liters"
    assert data["completed"] is False
    assert data["priority"] == 2
    assert "id" in data
    assert "owner_id" in data


def test_create_todo_without_token_is_rejected(client):
    response = client.post(
        "/api/v1/todos",
        json={
            "title": "Unauthorized todo",
            "description": "Should fail",
            "completed": False,
            "priority": 1
        }
    )

    assert response.status_code in [401, 403]

    data = response.json()
    assert "detail" in data


def test_get_single_todo_returns_200(client):
    user = create_test_user(client)
    headers = get_auth_headers(client, user)

    create_response = create_todo(
        client,
        headers,
        title="Read book",
        description="Read 20 pages",
        completed=False,
        priority=2
    )

    assert create_response.status_code == 201
    todo_id = create_response.json()["id"]

    response = client.get(f"/api/v1/todos/{todo_id}", headers=headers)

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == todo_id
    assert data["title"] == "Read book"
    assert data["description"] == "Read 20 pages"
    assert data["completed"] is False
    assert data["priority"] == 2


def test_get_nonexistent_todo_returns_404(client):
    user = create_test_user(client)
    headers = get_auth_headers(client, user)

    response = client.get("/api/v1/todos/999999", headers=headers)

    assert response.status_code == 404

    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Todo not found"


def test_get_other_users_todo_is_rejected(client):
    user1 = create_test_user(client)
    headers1 = get_auth_headers(client, user1)

    user2 = create_test_user(client)
    headers2 = get_auth_headers(client, user2)

    create_response = create_todo(
        client,
        headers1,
        title="Private todo",
        description="Only for user1"
    )

    assert create_response.status_code == 201
    todo_id = create_response.json()["id"]

    response = client.get(f"/api/v1/todos/{todo_id}", headers=headers2)

    assert response.status_code == 404

    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Todo not found"


def test_update_todo_success(client):
    user = create_test_user(client)
    headers = get_auth_headers(client, user)

    create_response = create_todo(
        client,
        headers,
        title="Old title",
        description="Old description",
        completed=False,
        priority=1
    )

    assert create_response.status_code == 201
    todo_id = create_response.json()["id"]

    response = client.put(
        f"/api/v1/todos/{todo_id}",
        headers=headers,
        json={
            "title": "New title",
            "description": "New description",
            "completed": True,
            "priority": 3
        }
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == todo_id
    assert data["title"] == "New title"
    assert data["description"] == "New description"
    assert data["completed"] is True
    assert data["priority"] == 3


def test_update_nonexistent_todo_returns_404(client):
    user = create_test_user(client)
    headers = get_auth_headers(client, user)

    response = client.put(
        "/api/v1/todos/999999",
        headers=headers,
        json={
            "title": "Does not matter",
            "description": "No todo",
            "completed": True,
            "priority": 2
        }
    )

    assert response.status_code == 404

    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Todo not found"


def test_update_other_users_todo_is_rejected(client):
    user1 = create_test_user(client)
    headers1 = get_auth_headers(client, user1)

    user2 = create_test_user(client)
    headers2 = get_auth_headers(client, user2)

    create_response = create_todo(
        client,
        headers1,
        title="User1 private todo",
        description="Only user1 can update this"
    )

    assert create_response.status_code == 201
    todo_id = create_response.json()["id"]

    response = client.put(
        f"/api/v1/todos/{todo_id}",
        headers=headers2,
        json={
            "title": "Hacked title",
            "description": "Should not update",
            "completed": True,
            "priority": 5
        }
    )

    assert response.status_code == 404

    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Todo not found"

def test_delete_todo_success_returns_204(client):
    user = create_test_user(client)
    headers = get_auth_headers(client, user)

    create_response = create_todo(
        client,
        headers,
        title="Todo to delete",
        description="Will be removed"
    )

    assert create_response.status_code == 201
    todo_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/todos/{todo_id}", headers=headers)

    assert delete_response.status_code == 204
    assert delete_response.text == ""

    get_response = client.get(f"/api/v1/todos/{todo_id}", headers=headers)
    assert get_response.status_code == 404


def test_delete_nonexistent_todo_returns_404(client):
    user = create_test_user(client)
    headers = get_auth_headers(client, user)

    response = client.delete("/api/v1/todos/999999", headers=headers)

    assert response.status_code == 404

    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Todo not found"


def test_delete_other_users_todo_is_rejected(client):
    user1 = create_test_user(client)
    headers1 = get_auth_headers(client, user1)

    user2 = create_test_user(client)
    headers2 = get_auth_headers(client, user2)

    create_response = create_todo(
        client,
        headers1,
        title="User1 todo to protect",
        description="User2 must not delete it"
    )

    assert create_response.status_code == 201
    todo_id = create_response.json()["id"]

    response = client.delete(f"/api/v1/todos/{todo_id}", headers=headers2)

    assert response.status_code == 404

    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Todo not found"