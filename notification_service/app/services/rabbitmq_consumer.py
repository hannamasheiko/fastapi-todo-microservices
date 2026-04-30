import pika
import logging
import time
from typing import Callable
from notification_service.app.config import settings

logger = logging.getLogger(__name__)


class RabbitMQConsumer:
    """Консюмер для отримання повідомлень з RabbitMQ"""

    def __init__(self, host: str = None, port: int = None):
        """Ініціалізація"""
        self.host = host or settings.rabbitmq_host
        self.port = port or settings.rabbitmq_port
        self.connection = None
        self.channel = None

    def connect(self):
        """Підключаємось до RabbitMQ"""
        try:
            credentials = pika.PlainCredentials(
                settings.rabbitmq_user,
                settings.rabbitmq_password
            )
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            logger.info("Consumer connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {repr(e)}")
            raise

    def is_connected(self) -> bool:
        """Перевіряємо, що connection і channel живі"""
        return (
            self.connection is not None
            and self.channel is not None
            and self.connection.is_open
            and self.channel.is_open
        )

    def ensure_connection(self):
        """Гарантуємо активне з'єднання з RabbitMQ"""
        if not self.is_connected():
            logger.warning("RabbitMQ consumer connection/channel is closed. Reconnecting...")
            self.close()
            self.connect()

    def declare_queue(self, queue_name: str, durable: bool = True):
        """Декларуємо чергу"""
        self.ensure_connection()

        self.channel.queue_declare(
            queue=queue_name,
            durable=durable,
            auto_delete=False
        )
        logger.info(f"Queue '{queue_name}' declared")

    def consume(self, queue_name: str, callback: Callable):
        """
        Слухаємо чергу і обробляємо повідомлення.
        Якщо connection падає — намагаємось перепідключитися і продовжити.
        """
        while True:
            try:
                self.ensure_connection()
                self.declare_queue(queue_name)

                self.channel.basic_qos(prefetch_count=1)
                self.channel.basic_consume(
                    queue=queue_name,
                    on_message_callback=callback,
                    auto_ack=False
                )

                logger.info(f"Started consuming from queue: {queue_name}")
                self.channel.start_consuming()

            except Exception as e:
                logger.error(f"Consumer error on queue '{queue_name}': {repr(e)}")
                self.close()
                time.sleep(5)
                logger.info(f"Retrying consumer connection for queue '{queue_name}'...")

    def close(self):
        """Закриваємо з'єднання"""
        try:
            if self.channel and self.channel.is_open:
                self.channel.close()
        except Exception:
            pass

        try:
            if self.connection and self.connection.is_open:
                self.connection.close()
        except Exception:
            pass

        self.channel = None
        self.connection = None
        logger.info("Closed RabbitMQ consumer connection")