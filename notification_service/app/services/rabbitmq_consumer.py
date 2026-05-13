import logging
from collections.abc import Awaitable, Callable

import aio_pika
from aio_pika.abc import AbstractIncomingMessage, AbstractRobustQueue

from notification_service.app.config import settings

logger = logging.getLogger(__name__)


MessageHandler = Callable[[AbstractIncomingMessage], Awaitable[None]]


class RabbitMQConsumer:
    """Асинхронний консюмер для отримання повідомлень з RabbitMQ."""

    def __init__(self, host: str | None = None, port: int | None = None):
        """Ініціалізація параметрів підключення."""
        self.host = host or settings.rabbitmq_host
        self.port = port or settings.rabbitmq_port
        self.connection: aio_pika.RobustConnection | None = None
        self.channel: aio_pika.RobustChannel | None = None
        self.queues: dict[str, AbstractRobustQueue] = {}

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
            await self.channel.set_qos(prefetch_count=1)

            logger.info("Consumer connected to RabbitMQ")

        except Exception as e:
            logger.error("Failed to connect to RabbitMQ: %s", repr(e))
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
        """Гарантуємо активне з'єднання з RabbitMQ."""
        if not self.is_connected():
            logger.warning(
                "RabbitMQ consumer connection/channel is closed. Reconnecting..."
            )
            await self.close()
            await self.connect()

    async def declare_queue(
        self,
        queue_name: str,
        durable: bool = True,
    ) -> AbstractRobustQueue:
        """Декларуємо чергу."""
        await self.ensure_connection()

        queue = await self.channel.declare_queue(
            name=queue_name,
            durable=durable,
            auto_delete=False,
        )

        self.queues[queue_name] = queue

        logger.info("Queue '%s' declared", queue_name)

        return queue

    async def consume(
        self,
        queue_name: str,
        callback: MessageHandler,
    ) -> None:
        """Слухаємо чергу і передаємо повідомлення в async callback."""
        queue = await self.declare_queue(queue_name)

        await queue.consume(callback, no_ack=False)

        logger.info("Started consuming from queue: %s", queue_name)

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

        self.queues = {}
        self.channel = None
        self.connection = None

        logger.info("Closed RabbitMQ consumer connection")
