from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from todo_service.app.config import settings

# Створюємо engine для PostgreSQL
engine = create_engine(
    settings.database_url,
    echo=settings.debug,  # Вивід SQL запитів в консоль
    pool_pre_ping=True,   # Перевіряє зв'язок перед запитом
    pool_size=10,         # Розмір пула з'єднань
    max_overflow=20       # Максимум додаткових з'єднань
)

# SessionLocal для отримання сесій БД
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base для всіх моделей
Base = declarative_base()

# Залежність для FastAPI
def get_db():
    """Залежність для отримання сесії БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()