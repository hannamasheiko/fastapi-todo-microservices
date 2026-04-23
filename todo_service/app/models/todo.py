from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from todo_service.app.database import Base
from datetime import datetime


class TodoItem(Base):
    """Модель завдання"""
    __tablename__ = "todo_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(1000))
    completed = Column(Boolean, default=False)
    priority = Column(Integer, default=0)  # 0=low, 1=medium, 2=high
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Зв'язок з користувачем
    owner = relationship("User", back_populates="todos")

    def __repr__(self):
        return f"<TodoItem(id={self.id}, title={self.title})>"