import pika
import json
import logging
from typing import Callable
import os

logger = logging.getLogger(__name__)


class RabbitMQConsumer:
    """Консюмер для отримання повідомлень з RabbitMQ"""

    def __init__(self, host: str = None, port: int = 5672):
        """Ініціалізація"""
        self.host = host or os.getenv("RABBITMQ_HOST", "localhost")
        self.port = port
        self.connection = None
        self.channel = None

    def connect(self):
        """Підключаємось до RabbitMQ"""
        try:
            credentials = pika.PlainCredentials('guest', 'guest')
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials,
                heartbeat=600
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            logger.info("Consumer connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            raise

    def declare_queue(self, queue_name: str, durable: bool = True):
        """Декларуємо чергу"""
        if not self.channel:
            self.connect()

        self.channel.queue_declare(
            queue=queue_name,
            durable=durable,
            auto_delete=False
        )

    def consume(self, queue_name: str, callback: Callable):
        """Слухаємо чергу і обробляємо повідомлення"""
        if not self.channel:
            self.connect()

        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=False
        )

        logger.info(f"Started consuming from queue: {queue_name}")
        self.channel.start_consuming()

    def close(self):
        """Закриваємо з'єднання"""
        if self.channel:
            self.channel.stop_consuming()
        if self.connection:
            self.connection.close()