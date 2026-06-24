from fastapi import APIRouter

from ai_service.app.schemas.tasks import ParsedTodoItem, TaskParseRequest
from ai_service.app.services.task_parser import task_parser_service


router = APIRouter(
    prefix="/ai/tasks",
    tags=["AI Tasks"],
)


@router.post("/parse", response_model=ParsedTodoItem)
def parse_task(request: TaskParseRequest) -> ParsedTodoItem:
    """Parse natural language text into a TodoItemCreate-compatible object."""
    return task_parser_service.parse_task(request.text)