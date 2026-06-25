from fastapi import APIRouter, Header, HTTPException, status

from ai_service.app.schemas.tasks import ParsedTodoItem, TaskParseRequest
from ai_service.app.services.task_parser import task_parser_service
from ai_service.app.services.todo_client import todo_client


router = APIRouter(
    prefix="/ai/tasks",
    tags=["AI Tasks"],
)


@router.post("/parse", response_model=ParsedTodoItem)
def parse_task(request: TaskParseRequest) -> ParsedTodoItem:
    """Parse natural language text into a TodoItemCreate-compatible object."""
    return task_parser_service.parse_task(request.text)


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_task_from_text(
    request: TaskParseRequest,
    authorization: str | None = Header(default=None),
) -> dict:
    """
    Parse natural language text with AI and create a real todo item in Todo Service.

    This endpoint expects the same JWT Authorization header that Todo Service uses.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required.",
        )

    parsed_task = task_parser_service.parse_task(request.text)

    created_todo = await todo_client.create_todo(
        todo=parsed_task,
        authorization=authorization,
    )

    return created_todo