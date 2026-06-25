import os
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

# Set test environment variables before importing the FastAPI app.
# This prevents OpenAIClient initialization from failing during tests.
os.environ.setdefault("OPENAI_API_KEY", "test-openai-api-key")
os.environ.setdefault("OPENAI_MODEL", "gpt-5-nano")
os.environ.setdefault("TODO_SERVICE_URL", "http://testserver")

from ai_service.app.main import app
from ai_service.app.schemas.tasks import ParsedTodoItem


client = TestClient(app)


def test_parse_task_success():
    """Test successful natural language task parsing."""
    parsed_task = ParsedTodoItem(
        title="Call the dentist",
        description="Tomorrow at 10, call the dentist to ask about appointment prices.",
        completed=False,
        priority=2,
    )

    with patch(
        "ai_service.app.routes.tasks.task_parser_service.parse_task",
        return_value=parsed_task,
    ):
        response = client.post(
            "/ai/tasks/parse",
            json={
                "text": "Tomorrow at 10 call the dentist and ask about appointment prices"
            },
        )

    assert response.status_code == 200
    assert response.json() == {
        "title": "Call the dentist",
        "description": "Tomorrow at 10, call the dentist to ask about appointment prices.",
        "completed": False,
        "priority": 2,
    }


def test_parse_task_validation_error():
    """Test validation error for too short task text."""
    response = client.post(
        "/ai/tasks/parse",
        json={"text": "ok"},
    )

    assert response.status_code == 422


def test_create_task_without_auth_returns_401():
    """Test that task creation requires Authorization header."""
    response = client.post(
        "/ai/tasks/create",
        json={"text": "Tomorrow at 10 call the dentist"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Authorization header is required."


def test_create_task_success():
    """Test successful AI parsing and todo creation flow."""
    parsed_task = ParsedTodoItem(
        title="Call the dentist",
        description="Tomorrow at 10, call the dentist to ask about appointment prices.",
        completed=False,
        priority=2,
    )

    created_todo = {
        "title": "Call the dentist",
        "description": "Tomorrow at 10, call the dentist to ask about appointment prices.",
        "completed": False,
        "priority": 2,
        "id": 28,
        "owner_id": 1,
        "created_at": "2026-06-25T08:58:24.997777Z",
        "updated_at": "2026-06-25T08:58:24.997777Z",
    }

    with patch(
        "ai_service.app.routes.tasks.task_parser_service.parse_task",
        return_value=parsed_task,
    ) as mock_parse_task, patch(
        "ai_service.app.routes.tasks.todo_client.create_todo",
        new_callable=AsyncMock,
        return_value=created_todo,
    ) as mock_create_todo:
        response = client.post(
            "/ai/tasks/create",
            json={
                "text": "Tomorrow at 10 call the dentist and ask about appointment prices"
            },
            headers={"Authorization": "Bearer test-token"},
        )

    assert response.status_code == 201
    assert response.json() == created_todo

    mock_parse_task.assert_called_once_with(
        "Tomorrow at 10 call the dentist and ask about appointment prices"
    )
    mock_create_todo.assert_awaited_once_with(
        todo=parsed_task,
        authorization="Bearer test-token",
    )