from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from notification_service.app.database import get_db
from notification_service.app.models import Notification
from notification_service.app.schemas import (
    NotificationCreateSchema,
    NotificationResponseSchema,
)


router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post("/send", response_model=NotificationResponseSchema)
def send_notification(
    notification: NotificationCreateSchema,
    db: Session = Depends(get_db),
):
    """Create notification for user."""

    db_notification = Notification(
        user_id=notification.user_id,
        title=notification.title,
        message=notification.message,
        type=notification.type,
        is_read=False,
    )

    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)

    return db_notification


@router.get("/user/{user_id}",response_model=List[NotificationResponseSchema],)
def get_user_notifications(
    user_id: int,
    db: Session = Depends(get_db),):
    """Get user notifications from database."""

    notifications = (
        db.query(Notification)
        .filter(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .all()
    )

    return notifications

@router.post("/task-completed/{user_id}/{task_title}",response_model=NotificationResponseSchema,)
def notify_task_completed(
    user_id: int,
    task_title: str,
    db: Session = Depends(get_db),):
    """Create task completed notification."""

    db_notification = Notification(
        user_id=user_id,
        title="Завдання виконане! ✅",
        message=f'Ви виконали завдання: "{task_title}"',
        type="success",
        is_read=False,
    )

    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)

    return db_notification