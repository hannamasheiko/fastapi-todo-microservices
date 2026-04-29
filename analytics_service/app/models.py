from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class UserAnalytics(Base):
    """Аналітика користувача"""
    __tablename__ = "user_analytics"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, unique=True, index=True)
    username = Column(String(50), nullable=True)
    total_todos = Column(Integer, nullable=False, default=0)
    completed_todos = Column(Integer, nullable=False, default=0)
    completion_rate = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())