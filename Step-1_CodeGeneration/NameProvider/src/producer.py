"""
RabbitMQ producer wrapper with best practices.
"""
import json
import logging
import pika
from .models import Person


class PersonProducer:
    """
    Wrapper for RabbitMQ producer with genealogy-specific configuration.

    Implements best practices:
    - JSON serialization
    - Persistent messages (survive broker restart)
    - Connection management
    - Graceful shutdown
    """

    def __init__(self, host: str, port: int, user: str, password: str, queue_name: str):
        """
        Initialize the RabbitMQ producer.

        Args:
            host: RabbitMQ server hostname
            port: RabbitMQ server port (default 5672)
            user: RabbitMQ username
            password: RabbitMQ password
            queue_name: Queue name for person records
        """
        self.queue_name = queue_name
        self.logger = logging.getLogger("name-provider.producer")

        # Create connection
        credentials = pika.PlainCredentials(user, password)
        parameters = pika.ConnectionParameters(
            host=host,
            port=port,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )

        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

        # Declare queue (idempotent - creates if doesn't exist)
        self.channel.queue_declare(
            queue=queue_name,
            durable=True  # Queue survives broker restart
        )

        self.logger.info(f"Producer initialized for queue: {queue_name}")

    def send(self, person: Person) -> bool:
        """
        Send a Person record to RabbitMQ.

        Args:
            person: Person model instance to send

        Returns:
            bool: True if send successful, False otherwise
        """
        try:
            # Convert Pydantic model to JSON
            person_json = person.model_dump_json()

            # Publish to queue
            self.channel.basic_publish(
                exchange='',  # Default exchange (direct to queue)
                routing_key=self.queue_name,
                body=person_json,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Persistent message
                    content_type='application/json'
                )
            )

            self.logger.debug(f"Sent record {person.recordId} to queue")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send record {person.recordId}: {e}")
            return False

    def close(self):
        """
        Close the producer connection gracefully.
        """
        self.logger.info("Closing producer...")
        if self.connection and not self.connection.is_closed:
            self.connection.close()
        self.logger.info("Producer closed")
