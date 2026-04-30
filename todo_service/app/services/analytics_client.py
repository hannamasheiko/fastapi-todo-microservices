import logging

import httpx
from sqlalchemy.orm import Session

from todo_service.app.models import TodoItem, User
from todo_service.app.config import settings


logger = logging.getLogger(__name__)


def sync_user_analytics(db: Session, user: User) -> None:
    """
    Recalculate user's todo statistics and send them to analytics_service.

    This function should not break the main todo operation if analytics_service is unavailable.
    """

    total_todos = (
        db.query(TodoItem)
        .filter(TodoItem.owner_id == user.id)
        .count()
    )

    completed_todos = (
        db.query(TodoItem)
        .filter(
            TodoItem.owner_id == user.id,
            TodoItem.completed.is_(True),
        )
        .count()
    )

    payload = {
        "username": user.username,
        "total_todos": total_todos,
        "completed_todos": completed_todos,
    }

    url = f"{settings.analytics_service_url}/analytics/user/{user.id}/sync"

    try:
        response = httpx.post(url, json=payload, timeout=3.0)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.warning(
            "Failed to sync analytics for user_id=%s: %s",
            user.id,
            exc,
        )