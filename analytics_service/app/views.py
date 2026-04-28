from fastapi import APIRouter
from datetime import datetime, UTC

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/user/{user_id}")
def get_user_analytics(user_id: int):
    """Отримати аналітику користувача"""
    return {
        "user_id": user_id,
        "total_todos": 15,
        "completed_todos": 10,
        "completion_rate": 67,
        "last_updated": datetime.now(UTC)
    }


@router.post("/user/{user_id}/sync")
def sync_user_analytics(user_id: int, total: int, completed: int):
    """Синхронізувати аналітику (викликається з todo service)"""
    completion_rate = int((completed / max(total, 1)) * 100)

    return {
        "user_id": user_id,
        "total_todos": total,
        "completed_todos": completed,
        "completion_rate": completion_rate,
        "synced_at": datetime.now(UTC)
    }