from fastapi import APIRouter
from notification_service.app.schemas import NotificationSchema
from typing import List
from datetime import datetime,UTC
from notification_service.app.storage import notifications_store

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post("/send")
def send_notification(notification: NotificationSchema):
    """Відправити повідомлення користувачу"""
    user_id = notification.user_id

    if user_id not in notifications_store:
        notifications_store[user_id] = []

    notif = {
        **notification.model_dump(),
        "created_at": datetime.now(UTC),
        "id": len(notifications_store[user_id]) + 1
    }

    notifications_store[user_id].append(notif)

    return {"status": "sent", "notification": notif}


@router.get("/user/{user_id}", response_model=List[NotificationSchema])
def get_user_notifications(user_id: int):
    """Отримати повідомлення користувача"""
    return notifications_store.get(user_id, [])


@router.post("/task-completed/{user_id}/{task_title}")
def notify_task_completed(user_id: int, task_title: str):
    """Повідомити про виконання завдання (викликається з todo service)"""
    notification = {
        "user_id": user_id,
        "title": "Завдання виконане! ✅",
        "message": f'Ви виконали завдання: "{task_title}"',
        "type": "success",
        "is_read": False,
        "created_at": datetime.now(UTC)
    }

    if user_id not in notifications_store:
        notifications_store[user_id] = []

    notifications_store[user_id].append(notification)

    return notification