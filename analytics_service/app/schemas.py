from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserAnalyticsSyncSchema(BaseModel):
    """Request schema for syncing user analytics."""

    username: str | None = None
    total_todos: int = Field(ge=0)
    completed_todos: int = Field(ge=0)


class UserAnalyticsSchema(BaseModel):
    """Response schema for user analytics."""

    id: int
    user_id: int
    username: str | None = None
    total_todos: int
    completed_todos: int
    completion_rate_percent: float = Field(
        description="Percentage of completed todos, rounded to 2 decimal places"
    )
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
