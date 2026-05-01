import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


os.environ.setdefault(
    "NOTIFICATION_DATABASE_URL",
    "postgresql://notification_user:notification_password_123@localhost:5434/notification_db",
)


from notification_service.app import main as notification_main
from notification_service.app.database import get_db
from notification_service.app.models import Base, Notification


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session, monkeypatch):
    monkeypatch.setattr(notification_main, "start_consumers", lambda: None)

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    notification_main.app.dependency_overrides[get_db] = override_get_db

    with TestClient(notification_main.app) as test_client:
        yield test_client

    notification_main.app.dependency_overrides.clear()


def test_notification_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "notifications",
    }


def test_get_user_notifications_returns_empty_list(client):
    response = client.get("/notifications/user/1")

    assert response.status_code == 200
    assert response.json() == []


def test_get_user_notifications_returns_existing_notifications(client, db_session):
    notification = Notification(
        user_id=1,
        title="Saved notification",
        message="This notification should be returned",
        type="info",
        is_read=False,
    )

    db_session.add(notification)
    db_session.commit()
    db_session.refresh(notification)

    response = client.get("/notifications/user/1")

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


def test_get_user_notifications_filters_by_user_id(client, db_session):
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
    db_session.commit()

    response = client.get("/notifications/user/1")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["user_id"] == 1
    assert data[0]["title"] == "User 1 notification"
    assert data[0]["message"] == "Message for user 1"