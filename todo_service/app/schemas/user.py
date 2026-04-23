from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# ==================== USER SCHEMAS ====================

class UserBase(BaseModel):
    """Базова схема користувача"""
    username: str
    email: EmailStr

class UserCreate(UserBase):
    """Схема для реєстрації"""
    password: str

class UserInDB(UserBase):
    """Схема користувача для повернення"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ==================== TOKEN SCHEMAS ====================

class Token(BaseModel):
    """Схема JWT токена"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Дані з JWT токена"""
    username: Optional[str] = None