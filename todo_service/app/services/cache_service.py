import json
import logging
from typing import Any, Optional

import redis.asyncio as redis

from todo_service.app.config import settings


logger = logging.getLogger(__name__)


class CacheService:
    """Сервіс для роботи з Redis кешем."""

    def __init__(self):
        """Ініціалізація асинхронного Redis клієнта."""
        self.redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            decode_responses=True,  # Повертає строки замість bytes
            socket_connect_timeout=5,
            socket_keepalive=True,
        )

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """Зберігаємо значення в Redis."""
        try:
            ttl = ttl or settings.cache_ttl
            serialized_value = json.dumps(value)

            await self.redis_client.setex(
                key,
                ttl,
                serialized_value,
            )

            logger.info("Cache SET: %s (TTL: %ss)", key, ttl)
            return True

        except Exception as e:
            logger.error("Cache SET error: %s", e)
            return False

    async def get(self, key: str) -> Optional[Any]:
        """Отримуємо значення з Redis."""
        try:
            value = await self.redis_client.get(key)

            if value:
                logger.info("Cache HIT: %s", key)
                return json.loads(value)

            logger.info("Cache MISS: %s", key)
            return None

        except Exception as e:
            logger.error("Cache GET error: %s", e)
            return None

    async def delete(self, key: str) -> bool:
        """Видаляємо значення з Redis."""
        try:
            await self.redis_client.delete(key)

            logger.info("Cache DELETE: %s", key)
            return True

        except Exception as e:
            logger.error("Cache DELETE error: %s", e)
            return False

    async def clear_all(self) -> bool:
        """Очищуємо весь кеш."""
        try:
            await self.redis_client.flushdb()

            logger.info("Cache CLEARED")
            return True

        except Exception as e:
            logger.error("Cache CLEAR error: %s", e)
            return False

    async def health_check(self) -> bool:
        """Перевіряємо з'єднання з Redis."""
        try:
            return await self.redis_client.ping()

        except Exception as e:
            logger.error("Redis health check failed: %s", e)
            return False

    async def get_info(self) -> dict:
        """Отримуємо інформацію про Redis."""
        try:
            return await self.redis_client.info()

        except Exception as e:
            logger.error("Redis INFO error: %s", e)
            return {}


# Глобальна інстанція кеша
cache_service = CacheService()