from fastapi import APIRouter
from todo_service.app.views.auth import router as auth_router
from todo_service.app.views.todos import router as todos_router
import httpx

# Основний API роутер
api_router = APIRouter(prefix="/api/v1")

# Підключаємо всі роутери
api_router.include_router(auth_router)
api_router.include_router(todos_router)

# Проксі до інших сервісів
@api_router.get("/analytics/user/{user_id}")
async def proxy_analytics(user_id: int):
    """Проксі до analytics сервісу"""
    async with httpx.AsyncClient() as client:
        # for local
        response = await client.get(f"http://localhost:8001/analytics/user/{user_id}")
        # for docker
        # response = await client.get(f"http://analytics_service:8000/analytics/user/{user_id}")

        return response.json()

@api_router.get("/notifications/user/{user_id}")
async def proxy_notifications(user_id: int):
    """Проксі до notification сервісу"""
    async with httpx.AsyncClient() as client:
        # for local
        response = await client.get(f"http://localhost:8002/notifications/user/{user_id}")
        # for docker
        # response = await client.get(f"http://notification_service:8000/notifications/user/{user_id}")
        return response.json()



__all__ = ["api_router"]