import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from analytics_service.app.database import get_db
from analytics_service.app.main import app
from analytics_service.app.models import Base

pytestmark = pytest.mark.anyio

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


@pytest.fixture()
def anyio_backend():
    return "asyncio"


@pytest.fixture()
async def db_session():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)


@pytest.fixture()
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as test_client:
        yield test_client

    app.dependency_overrides.clear()


async def test_analytics_health_check(client):
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "analytics",
    }


async def test_get_analytics_not_found(client):
    response = await client.get("/analytics/user/999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Analytics not found",
    }


async def test_sync_user_analytics_creates_record(client):
    payload = {
        "username": "alice",
        "total_todos": 13,
        "completed_todos": 1,
    }

    response = await client.post("/analytics/user/1/sync", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["user_id"] == 1
    assert data["username"] == "alice"
    assert data["total_todos"] == 13
    assert data["completed_todos"] == 1
    assert data["completion_rate_percent"] == 7.69
    assert data["created_at"] is not None
    assert data["updated_at"] is not None


async def test_get_user_analytics_returns_existing_record(client):
    payload = {
        "username": "alice",
        "total_todos": 10,
        "completed_todos": 5,
    }

    await client.post("/analytics/user/1/sync", json=payload)

    response = await client.get("/analytics/user/1")

    assert response.status_code == 200

    data = response.json()

    assert data["user_id"] == 1
    assert data["username"] == "alice"
    assert data["total_todos"] == 10
    assert data["completed_todos"] == 5
    assert data["completion_rate_percent"] == 50.0


async def test_sync_user_analytics_updates_existing_record(client):
    initial_payload = {
        "username": "alice",
        "total_todos": 10,
        "completed_todos": 5,
    }

    updated_payload = {
        "username": "alice",
        "total_todos": 12,
        "completed_todos": 3,
    }

    first_response = await client.post(
        "/analytics/user/1/sync",
        json=initial_payload,
    )
    second_response = await client.post(
        "/analytics/user/1/sync",
        json=updated_payload,
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    first_data = first_response.json()
    second_data = second_response.json()

    assert second_data["id"] == first_data["id"]
    assert second_data["user_id"] == 1
    assert second_data["username"] == "alice"
    assert second_data["total_todos"] == 12
    assert second_data["completed_todos"] == 3
    assert second_data["completion_rate_percent"] == 25.0


async def test_sync_user_analytics_with_zero_todos(client):
    payload = {
        "username": "alice",
        "total_todos": 0,
        "completed_todos": 0,
    }

    response = await client.post("/analytics/user/1/sync", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["total_todos"] == 0
    assert data["completed_todos"] == 0
    assert data["completion_rate_percent"] == 0.0
