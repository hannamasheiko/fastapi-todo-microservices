import httpx
from fastapi import HTTPException, status

from ai_service.app.config import settings
from ai_service.app.schemas.tasks import ParsedTodoItem


class TodoClient:
    """HTTP client for communicating with Todo Service."""

    def __init__(self) -> None:
        self.base_url = settings.todo_service_url.rstrip("/")

    async def create_todo(
        self,
        todo: ParsedTodoItem,
        authorization: str,
    ) -> dict:
        """
        Create a todo item in Todo Service.

        The todo data is already parsed by AI and is compatible
        with TodoItemCreate in todo_service.
        """
        url = f"{self.base_url}/api/v1/todos"

        headers = {
            "Authorization": authorization,
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    url,
                    json=todo.model_dump(),
                    headers=headers,
                )

        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Todo Service is unavailable.",
            ) from exc

        if response.status_code >= 400:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json() if response.content else response.text,
            )

        return response.json()


todo_client = TodoClient()