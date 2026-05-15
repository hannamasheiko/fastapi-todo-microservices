import json
import logging
import os
from typing import Any, Dict

import aio_pika

from todo_service.app.config import settings

logger = logging.getLogger(__name__)


class RabbitMQProducer:
    """Асинхронний продюсер для відправки повідомлень у RabbitMQ."""

    def __init__(self, host: str | None = None, port: int = 5672):
        """Ініціалізація параметрів з'єднання."""
        self.host = host or os.getenv("RABBITMQ_HOST", "localhost")
        self.port = port
        self.connection: aio_pika.RobustConnection | None = None
        self.channel: aio_pika.RobustChannel | None = None

    async def connect(self) -> None:
        """Підключаємось до RabbitMQ."""
        try:
            self.connection = await aio_pika.connect_robust(
                host=self.host,
                port=self.port,
                login=settings.rabbitmq_user,
                password=settings.rabbitmq_password,
                heartbeat=600,
                timeout=10,
            )

            self.channel = await self.connection.channel()

            logger.info("Connected to RabbitMQ")

        except Exception as e:
            logger.error("Failed to connect to RabbitMQ: %s", e)
            raise

    def is_connected(self) -> bool:
        """Перевіряємо, що connection і channel живі."""
        return (
            self.connection is not None
            and self.channel is not None
            and not self.connection.is_closed
            and not self.channel.is_closed
        )

    async def ensure_connection(self) -> None:
        """Гарантуємо, що з'єднання з RabbitMQ активне."""
        if not self.is_connected():
            logger.warning("RabbitMQ connection/channel is closed. Reconnecting...")
            await self.close()
            await self.connect()

    async def declare_queue(
        self,
        queue_name: str,
        durable: bool = True,
    ) -> None:
        """Створюємо чергу."""
        await self.ensure_connection()

        await self.channel.declare_queue(
            name=queue_name,
            durable=durable,
            auto_delete=False,
        )

        logger.info("Queue '%s' declared", queue_name)

    async def publish_message(
        self,
        queue_name: str,
        message: Dict[str, Any],
        routing_key: str | None = None,
    ) -> None:
        """Відправляємо повідомлення в чергу."""
        await self.ensure_connection()

        body = json.dumps(message).encode("utf-8")

        aio_message = aio_pika.Message(
            body=body,
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            content_type="application/json",
        )

        target_routing_key = routing_key or queue_name

        try:
            await self.channel.default_exchange.publish(
                aio_message,
                routing_key=target_routing_key,
            )

            logger.info("Message published to %s: %s", queue_name, message)

        except Exception as e:
            logger.warning("Publish failed, trying to reconnect: %s", e)

            await self.close()
            await self.connect()

            await self.channel.default_exchange.publish(
                aio_message,
                routing_key=target_routing_key,
            )

            logger.info(
                "Message published to %s after reconnect: %s",
                queue_name,
                message,
            )

    async def close(self) -> None:
        """Закриваємо з'єднання."""
        try:
            if self.channel and not self.channel.is_closed:
                await self.channel.close()
        except Exception:
            pass

        try:
            if self.connection and not self.connection.is_closed:
                await self.connection.close()
        except Exception:
            pass

        self.channel = None
        self.connection = None

        logger.info("Closed RabbitMQ connection")


# Глобальна інстанція продюсера
producer = RabbitMQProducer()
