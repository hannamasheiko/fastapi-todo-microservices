from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NotificationSchema(BaseModel):
    """Схема повідомлення"""
    user_id: int
    title: str
    message: str
    type: str = "info"  # info, warning, success, error
    is_read: bool = False
    created_at: Optional[datetime] = None