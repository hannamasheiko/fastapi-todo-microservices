import json
import logging
from app.services.rabbitmq_consumer import RabbitMQConsumer
from app.storage import notifications_store

logger = logging.getLogger(__name__)

# Фейкова БД повідомлень
# notifications_store = {}


def task_completed_handler(ch, method, properties, body):
    """Обробляємо подію task:completed"""
    try:
        message = json.loads(body)
        logger.info(f"Received task_completed event: {message}")

        user_id = message.get("user_id")
        task_title = message.get("title")

        # Створюємо повідомлення
        notification = {
            "user_id": user_id,
            "title": "Завдання виконане! ✅",
            "message": f'Ви виконали завдання: "{task_title}"',
            "type": "success",
            "is_read": False,
            "created_at": message.get("timestamp")
        }

        # Зберігаємо в "БД"
        if user_id not in notifications_store:
            notifications_store[user_id] = []

        notifications_store[user_id].append(notification)
        logger.info(f"Notification created for user {user_id}")

        # Підтверджуємо обробку
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def task_created_handler(ch, method, properties, body):
    """Обробляємо подію task:created"""
    try:
        message = json.loads(body)
        logger.info(f"Received task_created event: {message}")

        user_id = message.get("user_id")
        task_title = message.get("title")

        # Інформаційне повідомлення
        notification = {
            "user_id": user_id,
            "title": "Нове завдання 📝",
            "message": f'Ви створили завдання: "{task_title}"',
            "type": "info",
            "is_read": False,
            "created_at": message.get("timestamp")
        }

        if user_id not in notifications_store:
            notifications_store[user_id] = []

        notifications_store[user_id].append(notification)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def start_consumers():
    """Запускаємо консюмерів"""
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