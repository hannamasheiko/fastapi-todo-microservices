from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NotificationCreateSchema(BaseModel):
    """Request schema for creating a notification."""

    user_id: int
    title: str = Field(max_length=200)
    message: str
    type: str = "info"


class NotificationResponseSchema(BaseModel):
    """Response schema for notification."""

    id: int
    user_id: int
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
