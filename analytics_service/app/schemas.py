from pydantic import BaseModel
from datetime import datetime


class UserAnalyticsSchema(BaseModel):
    """Схема аналітики"""
    user_id: int
    username: str
    total_todos: int
    completed_todos: int
    completion_rate: int

    class Config:
        from_attributes = True