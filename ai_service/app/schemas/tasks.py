from pydantic import BaseModel, Field


class TaskParseRequest(BaseModel):
    """Request schema for parsing natural language into todo item data."""

    text: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="Natural language text that should be converted into todo item fields.",
        examples=["Tomorrow at 10 call the dentist and ask about appointment prices."],
    )


class ParsedTodoItem(BaseModel):
    """Parsed todo item data compatible with TodoItemCreate schema."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Todo title.",
        examples=["Call the dentist"],
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Todo description.",
        examples=["Tomorrow at 10 ask about appointment prices."],
    )
    completed: bool = Field(
        default=False,
        description="Todo completion status. Should be false for newly parsed tasks.",
        examples=[False],
    )
    priority: int = Field(
        default=0,
        ge=0,
        le=2,
        description="Todo priority: 0=low, 1=medium, 2=high.",
        examples=[2],
    )