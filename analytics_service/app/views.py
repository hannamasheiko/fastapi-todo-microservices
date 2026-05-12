from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from analytics_service.app.database import get_db
from analytics_service.app.models import UserAnalytics
from analytics_service.app.schemas import (
    UserAnalyticsSchema,
    UserAnalyticsSyncSchema,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def calculate_completion_rate_percent(
    total_todos: int,
    completed_todos: int,
) -> float:
    """Calculate completion rate as percent rounded to 2 decimal places."""
    if total_todos == 0:
        return 0.0

    return round((completed_todos / total_todos) * 100, 2)


@router.get(
    "/user/{user_id}",
    response_model=UserAnalyticsSchema,
)
async def get_user_analytics(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get saved analytics for a user from analytics_db."""

    result = await db.execute(
        select(UserAnalytics).where(UserAnalytics.user_id == user_id)
    )

    analytics = result.scalar_one_or_none()

    if analytics is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analytics not found",
        )

    return analytics


@router.post(
    "/user/{user_id}/sync",
    response_model=UserAnalyticsSchema,
)
async def sync_user_analytics(
    user_id: int,
    payload: UserAnalyticsSyncSchema,
    db: AsyncSession = Depends(get_db),
):
    """Create or update user analytics record in analytics_db."""

    completion_rate_percent = calculate_completion_rate_percent(
        total_todos=payload.total_todos,
        completed_todos=payload.completed_todos,
    )

    result = await db.execute(
        select(UserAnalytics).where(UserAnalytics.user_id == user_id)
    )

    analytics = result.scalar_one_or_none()

    if analytics is None:
        analytics = UserAnalytics(
            user_id=user_id,
            username=payload.username,
            total_todos=payload.total_todos,
            completed_todos=payload.completed_todos,
            completion_rate_percent=completion_rate_percent,
        )
        db.add(analytics)
    else:
        analytics.username = payload.username
        analytics.total_todos = payload.total_todos
        analytics.completed_todos = payload.completed_todos
        analytics.completion_rate_percent = completion_rate_percent
        analytics.updated_at = datetime.now(UTC)

    await db.commit()
    await db.refresh(analytics)

    return analytics
