import asyncio
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

TEST_DATABASE_URL = (
    "postgresql+asyncpg://todo_user:secure_password_123@localhost:5432/todo_test_db"
)

os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from todo_service.app.database import Base, get_db
from todo_service.app.main import app
from sqlalchemy.pool import NullPool


engine = create_async_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
    poolclass=NullPool,
)


TestingSessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


async def recreate_test_database():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)


async def drop_test_database():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session", autouse=True)
def prepare_test_database():
    """Підготувати чисту тестову базу перед запуском тестів."""
    asyncio.run(recreate_test_database())
    yield
    asyncio.run(drop_test_database())


@pytest.fixture()
def db_session():
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session

    return override_get_db


@pytest.fixture()
def client(db_session):
    app.dependency_overrides[get_db] = db_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()