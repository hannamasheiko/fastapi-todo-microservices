import pika
import json
from typing import Dict, Any
import logging
import os


logger = logging.getLogger(__name__)


class RabbitMQProducer:
    """Продюсер для відправки повідомлень в RabbitMQ"""

    def __init__(self, host: str = None, port: int = 5672):
        """Ініціалізація з'єднання"""
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
                heartbeat=600,
                blocked_connection_timeout=300
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            logger.info("Connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    def declare_queue(self, queue_name: str, durable: bool = True):
        """Створюємо чергу (queue)"""
        if not self.channel:
            self.connect()

        self.channel.queue_declare(
            queue=queue_name,
            durable=durable,
            auto_delete=False
        )
        logger.info(f"Queue '{queue_name}' declared")

    def publish_message(
            self,
            queue_name: str,
            message: Dict[str, Any],
            routing_key: str = None
    ):
        """Відправляємо повідомлення в чергу"""
        if not self.channel:
            self.connect()

        try:
            self.channel.basic_publish(
                exchange='',
                routing_key=routing_key or queue_name,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Persisten message
                    content_type='application/json'
                )
            )
            logger.info(f"Message published to {queue_name}: {message}")
        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            raise

    def close(self):
        """Закриваємо з'єднання"""
        if self.connection:
            self.connection.close()
            logger.info("Closed RabbitMQ connection")


# Глобальна інстанція продюсера
producer = RabbitMQProducer()