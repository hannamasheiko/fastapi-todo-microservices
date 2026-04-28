from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class TodoItemBase(BaseModel):
    """Базова схема завдання"""
    title: str
    description: Optional[str] = None
    completed: bool = False
    priority: int = 0

class TodoItemCreate(TodoItemBase):
    """Схема для створення завдання"""
    pass

class TodoItemUpdate(BaseModel):
    """Схема для оновлення завдання"""
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[int] = None

class TodoItemInDB(TodoItemBase):
    """Схема завдання для повернення"""
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)