from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from notification_service.app.config import settings
from sqlalchemy.pool import NullPool

# Створюємо async engine для PostgreSQL
engine = create_async_engine(
    settings.notification_database_url,
    pool_pre_ping=True,
    poolclass=NullPool,
)

# Об'єкт для створення асинхронних сесій БД
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


# Асинхронна залежність для FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Залежність для отримання асинхронної сесії БД."""
    async with AsyncSessionLocal() as session:
        yield session