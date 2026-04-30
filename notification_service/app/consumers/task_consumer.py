import json
import logging
from notification_service.app.database import SessionLocal
from notification_service.app.models import Notification
from notification_service.app.services.rabbitmq_consumer import RabbitMQConsumer

logger = logging.getLogger(__name__)


def create_notification(
    user_id: int,
    title: str,
    message: str,
    notification_type: str,
) -> None:
    """Create notification record in notification_db."""

    db = SessionLocal()

    try:
        db_notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=notification_type,
            is_read=False,
        )

        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)

        logger.info(
            "Notification created in DB: id=%s, user_id=%s",
            db_notification.id,
            user_id,
        )

    except Exception as exc:
        db.rollback()
        logger.error(
            "Failed to create notification for user_id=%s: %s",
            user_id,
            repr(exc),
        )
        raise

    finally:
        db.close()


def task_completed_handler(ch, method, properties, body):
    """Handle task:completed event."""

    try:
        message = json.loads(body)
        logger.info("Received task_completed event: %s", message)

        user_id = message.get("user_id")
        task_title = message.get("title")

        if user_id is None or not task_title:
            raise ValueError(f"Invalid task_completed payload: {message}")

        create_notification(
            user_id=user_id,
            title="Завдання виконане! ✅",
            message=f'Ви виконали завдання: "{task_title}"',
            notification_type="success",
        )

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as exc:
        logger.error("Error processing task_completed message: %s", repr(exc))
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def task_created_handler(ch, method, properties, body):
    """Handle task:created event."""

    try:
        message = json.loads(body)
        logger.info("Received task_created event: %s", message)

        user_id = message.get("user_id")
        task_title = message.get("title")

        if user_id is None or not task_title:
            raise ValueError(f"Invalid task_created payload: {message}")

        create_notification(
            user_id=user_id,
            title="Нове завдання",
            message=f'Ви створили завдання: "{task_title}"',
            notification_type="info",
        )

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as exc:
        logger.error("Error processing task_created message: %s", repr(exc))
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def start_consumers():
    """Start RabbitMQ consumers."""
    import threading

    def run_completed_consumer():
        consumer = RabbitMQConsumer()
        consumer.declare_queue("task:completed")
        consumer.consume("task:completed", task_completed_handler)

    def run_created_consumer():
        consumer = RabbitMQConsumer()
        consumer.declare_queue("task:created")
        consumer.consume("task:created", task_created_handler)

    thread1 = threading.Thread(target=run_completed_consumer, daemon=True)
    thread2 = threading.Thread(target=run_created_consumer, daemon=True)

    thread1.start()
    thread2.start()

    logger.info("RabbitMQ consumer threads started")