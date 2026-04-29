from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from analytics_service.app.database import get_db
from analytics_service.app.models import UserAnalytics
from analytics_service.app.schemas import (
    UserAnalyticsSchema,
    UserAnalyticsSyncSchema,
)


router = APIRouter(prefix="/analytics", tags=["Analytics"])


def calculate_completion_rate(total_todos: int, completed_todos: int) -> int:
    """Calculate completion rate as integer percent."""
    return int((completed_todos / max(total_todos, 1)) * 100)


@router.get(
    "/user/{user_id}",
    response_model=UserAnalyticsSchema,
)
def get_user_analytics(
    user_id: int,
    db: Session = Depends(get_db),
):
    """Get saved analytics for a user from analytics_db."""

    analytics = (
        db.query(UserAnalytics)
        .filter(UserAnalytics.user_id == user_id)
        .first()
    )

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
def sync_user_analytics(
    user_id: int,
    payload: UserAnalyticsSyncSchema,
    db: Session = Depends(get_db),
):
    """Create or update user analytics record in analytics_db."""

    completion_rate = calculate_completion_rate(
        total_todos=payload.total_todos,
        completed_todos=payload.completed_todos,
    )

    analytics = (
        db.query(UserAnalytics)
        .filter(UserAnalytics.user_id == user_id)
        .first()
    )

    if analytics is None:
        analytics = UserAnalytics(
            user_id=user_id,
            username=payload.username,
            total_todos=payload.total_todos,
            completed_todos=payload.completed_todos,
            completion_rate=completion_rate,
        )
        db.add(analytics)
    else:
        analytics.username = payload.username
        analytics.total_todos = payload.total_todos
        analytics.completed_todos = payload.completed_todos
        analytics.completion_rate = completion_rate
        analytics.updated_at = datetime.now(UTC)

    db.commit()
    db.refresh(analytics)

    return analytics