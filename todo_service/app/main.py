import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from todo_service.app.config import settings
from todo_service.app.routes import api_router
from todo_service.app.services.cache_service import cache_service
from todo_service.app.services.rabbitmq_producer import producer


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ініціалізація ресурсів при старті застосунку."""
    try:
        await producer.connect()
        await producer.declare_queue("task:created")
        await producer.declare_queue("task:completed")
    except Exception as e:
        logger.error("RabbitMQ startup init failed: %s", e)

    yield

    try:
        await producer.close()
    except Exception:
        pass


# Ініціалізуємо FastAPI
app = FastAPI(
    title="Todo API",
    description="REST API з MVC паттерном, PostgreSQL та мікросервісами",
    version="3.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Підключаємо API роутер
app.include_router(api_router)


# Статус endpoint
@app.get("/", tags=["Health"])
def read_root():
    """Перевірка статусу сервера."""
    return {
        "message": "Todo API is running!",
        "docs": "/docs",
        "version": "3.0.0",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check з перевіркою Redis."""
    redis_status = "healthy" if await cache_service.health_check() else "unhealthy"

    return {
        "status": "healthy",
        "redis": redis_status,
    }


@app.get("/cache/stats", tags=["Cache"])
async def cache_stats():
    """Статистика Redis кеша."""
    info = await cache_service.get_info()

    return {
        "used_memory": info.get("used_memory_human"),
        "connected_clients": info.get("connected_clients"),
        "total_commands_processed": info.get("total_commands_processed"),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "todo_service.app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )