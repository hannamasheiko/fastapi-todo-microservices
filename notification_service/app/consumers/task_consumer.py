import json
import logging

from aio_pika.abc import AbstractIncomingMessage

from notification_service.app.database import AsyncSessionLocal
from notification_service.app.models import Notification
from notification_service.app.services.rabbitmq_consumer import RabbitMQConsumer

logger = logging.getLogger(__name__)


async def create_notification(
    user_id: int,
    title: str,
    message: str,
    notification_type: str,
) -> None:
    """Створюємо запис повідомлення в notification_db."""

    async with AsyncSessionLocal() as db:
        try:
            db_notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                type=notification_type,
                is_read=False,
            )

            db.add(db_notification)

            await db.commit()
            await db.refresh(db_notification)

            logger.info(
                "Notification created in DB: id=%s, user_id=%s",
                db_notification.id,
                user_id,
            )

        except Exception as exc:
            await db.rollback()
            logger.error(
                "Failed to create notification for user_id=%s: %s",
                user_id,
                repr(exc),
            )
            raise


async def task_completed_handler(message: AbstractIncomingMessage) -> None:
    """Обробляємо подію task:completed."""

    try:
        payload = json.loads(message.body.decode("utf-8"))
        logger.info("Received task_completed event: %s", payload)

        user_id = payload.get("user_id")
        task_title = payload.get("title")

        if user_id is None or not task_title:
            raise ValueError(f"Invalid task_completed payload: {payload}")

        await create_notification(
            user_id=user_id,
            title="Завдання виконане! ✅",
            message=f'Ви виконали завдання: "{task_title}"',
            notification_type="success",
        )

        await message.ack()

    except Exception as exc:
        logger.error("Error processing task_completed message: %s", repr(exc))
        await message.reject(requeue=False)


async def task_created_handler(message: AbstractIncomingMessage) -> None:
    """Обробляємо подію task:created."""

    try:
        payload = json.loads(message.body.decode("utf-8"))
        logger.info("Received task_created event: %s", payload)

        user_id = payload.get("user_id")
        task_title = payload.get("title")

        if user_id is None or not task_title:
            raise ValueError(f"Invalid task_created payload: {payload}")

        await create_notification(
            user_id=user_id,
            title="Нове завдання",
            message=f'Ви створили завдання: "{task_title}"',
            notification_type="info",
        )

        await message.ack()

    except Exception as exc:
        logger.error("Error processing task_created message: %s", repr(exc))
        await message.reject(requeue=False)


async def start_consumers() -> RabbitMQConsumer:
    """Запускаємо RabbitMQ consumers."""

    consumer = RabbitMQConsumer()

    await consumer.connect()

    await consumer.consume(
        "task:completed",
        task_completed_handler,
    )

    await consumer.consume(
        "task:created",
        task_created_handler,
    )

    logger.info("RabbitMQ consumers started")

    return consumer
