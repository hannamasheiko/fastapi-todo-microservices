from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserAnalytics(Base):
    """Аналітика користувача"""
    __tablename__ = "user_analytics"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    username = Column(String(50))
    total_todos = Column(Integer, default=0)
    completed_todos = Column(Integer, default=0)
    completion_rate = Column(Integer, default=0)  # 0-100%
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())