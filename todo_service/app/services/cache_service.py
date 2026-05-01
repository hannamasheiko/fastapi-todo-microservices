import redis
import json
import logging
from typing import Any, Optional
from todo_service.app.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Сервіс для роботи з Redis кешем"""

    def __init__(self):
        """Ініціалізація Redis клієнта"""
        self.redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            decode_responses=True,  # Повертає строки замість bytes
            socket_connect_timeout=5,
            socket_keepalive=True
        )

    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Зберігаємо значення в Redis"""
        try:
            ttl = ttl or settings.cache_ttl
            serialized_value = json.dumps(value)
            self.redis_client.setex(
                key,
                ttl,
                serialized_value
            )
            logger.info(f"Cache SET: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Cache SET error: {e}")
            return False

    def get(self, key: str) -> Optional[Any]:
        """Отримуємо значення з Redis"""
        try:
            value = self.redis_client.get(key)
            if value:
                logger.info(f"Cache HIT: {key}")
                return json.loads(value)
            else:
                logger.info(f"Cache MISS: {key}")
                return None
        except Exception as e:
            logger.error(f"Cache GET error: {e}")
            return None

    def delete(self, key: str) -> bool:
        """Видаляємо значення з Redis"""
        try:
            self.redis_client.delete(key)
            logger.info(f"Cache DELETE: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache DELETE error: {e}")
            return False

    def clear_all(self) -> bool:
        """Очищуємо весь кеш"""
        try:
            self.redis_client.flushdb()
            logger.info("Cache CLEARED")
            return True
        except Exception as e:
            logger.error(f"Cache CLEAR error: {e}")
            return False

    def health_check(self) -> bool:
        """Перевіряємо з'єднання з Redis"""
        try:
            return self.redis_client.ping()
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False


# Глобальна інстанція кеша
cache_service = CacheService()