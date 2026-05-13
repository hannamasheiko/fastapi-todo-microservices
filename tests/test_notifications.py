import os

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

os.environ["NOTIFICATION_DATABASE_URL"] = (
    "postgresql+asyncpg://notification_user:notification_password_123@localhost:5434/notification_db"
)


from notification_service.app import main as notification_main
from notification_service.app.database import get_db
from notification_service.app.models import Base, Notification

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
async def client(db_session, monkeypatch):
    monkeypatch.setattr(notification_main, "start_consumers", lambda: None)

    async def override_get_db():
        yield db_session

    notification_main.app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=notification_main.app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as test_client:
        yield test_client

    notification_main.app.dependency_overrides.clear()


async def test_notification_health_check(client):
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "notifications",
    }


async def test_get_user_notifications_returns_empty_list(client):
    response = await client.get("/notifications/user/1")

    assert response.status_code == 200
    assert response.json() == []


async def test_get_user_notifications_returns_existing_notifications(
    client, db_session
):
    notification = Notification(
        user_id=1,
        title="Saved notification",
        message="This notification should be returned",
        type="info",
        is_read=False,
    )

    db_session.add(notification)
    await db_session.commit()
    await db_session.refresh(notification)

    response = await client.get("/notifications/user/1")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == notification.id
    assert data[0]["user_id"] == 1
    assert data[0]["title"] == "Saved notification"
    assert data[0]["message"] == "This notification should be returned"
    assert data[0]["type"] == "info"
    assert data[0]["is_read"] is False
    assert data[0]["created_at"] is not None


async def test_get_user_notifications_filters_by_user_id(client, db_session):
    first_notification = Notification(
        user_id=1,
        title="User 1 notification",
        message="Message for user 1",
        type="info",
        is_read=False,
    )

    second_notification = Notification(
        user_id=2,
        title="User 2 notification",
        message="Message for user 2",
        type="info",
        is_read=False,
    )

    db_session.add_all([first_notification, second_notification])
    await db_session.commit()

    response = await client.get("/notifications/user/1")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["user_id"] == 1
    assert data[0]["title"] == "User 1 notification"
    assert data[0]["message"] == "Message for user 1"
