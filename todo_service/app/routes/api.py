import httpx
from fastapi import APIRouter, HTTPException, status

from todo_service.app.config import settings
from todo_service.app.views.auth import router as auth_router
from todo_service.app.views.todos import router as todos_router

# Основний API роутер
api_router = APIRouter(prefix="/api/v1")

# Підключаємо всі роутери
api_router.include_router(auth_router)
api_router.include_router(todos_router)


# Проксі до інших сервісів
@api_router.get("/analytics/user/{user_id}")
async def proxy_analytics(user_id: int):
    """Проксі до analytics сервісу."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.analytics_service_url}/analytics/user/{user_id}",
                timeout=3.0,
            )
            response.raise_for_status()
            return response.json()

    except httpx.ConnectError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Analytics service is unavailable",
        )

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Analytics service error: {e.response.text}",
        )


@api_router.get("/notifications/user/{user_id}")
async def proxy_notifications(user_id: int):
    """Проксі до notification сервісу."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.notification_service_url}/notifications/user/{user_id}",
                timeout=3.0,
            )
            response.raise_for_status()
            return response.json()

    except httpx.ConnectError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Notification service is unavailable",
        )

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Notification service error: {e.response.text}",
        )


__all__ = ["api_router"]
