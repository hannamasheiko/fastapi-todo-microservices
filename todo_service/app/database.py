from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from todo_service.app.config import settings

# Створюємо async engine для PostgreSQL
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,  # Вивід SQL-запитів у консоль
    pool_pre_ping=True,  # Перевіряє з'єднання перед запитом
    pool_size=10,  # Розмір пулу з'єднань
    max_overflow=20,  # Максимум додаткових з'єднань
)

# Об'єкт для створення асинхронних сесій БД
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)

# Base для всіх моделей
Base = declarative_base()


# Асинхронна залежність для FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Залежність для отримання асинхронної сесії БД."""
    async with AsyncSessionLocal() as session:
        yield session
