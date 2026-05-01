from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional
from datetime import datetime

# ==================== USER SCHEMAS ====================

class UserBase(BaseModel):
    """Базова схема користувача"""
    username: str
    email: EmailStr

class UserCreate(UserBase):
    """Схема для реєстрації"""
    password: str = Field(min_length=8)

class UserInDB(UserBase):
    """Схема користувача для повернення"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ==================== TOKEN SCHEMAS ====================

class Token(BaseModel):
    """Схема JWT токена"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Дані з JWT токена"""
    username: Optional[str] = None