import logging

import httpx
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from todo_service.app.config import settings
from todo_service.app.models import TodoItem, User

logger = logging.getLogger(__name__)


async def sync_user_analytics(db: AsyncSession, user: User) -> None:
    """
    Recalculate user's todo statistics and send them to analytics_service.

    This function should not break the main todo operation if analytics_service is unavailable.
    """

    total_todos_result = await db.execute(
        select(func.count(TodoItem.id)).where(TodoItem.owner_id == user.id)
    )
    total_todos = total_todos_result.scalar_one()

    completed_todos_result = await db.execute(
        select(func.count(TodoItem.id)).where(
            TodoItem.owner_id == user.id,
            TodoItem.completed.is_(True),
        )
    )
    completed_todos = completed_todos_result.scalar_one()

    payload = {
        "username": user.username,
        "total_todos": total_todos,
        "completed_todos": completed_todos,
    }

    url = f"{settings.analytics_service_url}/analytics/user/{user.id}/sync"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                timeout=3.0,
            )
            response.raise_for_status()

    except httpx.HTTPError as exc:
        logger.warning(
            "Failed to sync analytics for user_id=%s: %s",
            user.id,
            exc,
        )
