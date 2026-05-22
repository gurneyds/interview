"""
Queue depth monitor with automatic replenishment.
"""
import logging
import threading
import pika
from .generator import PersonGenerator
from .producer import PersonProducer


class QueueMonitor:
    """
    Background thread that monitors RabbitMQ queue depth and produces records
    when the queue drops below the minimum threshold.

    Checks queue message count directly via RabbitMQ API.
    """

    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        queue_name: str,
        min_queue_size: int,
        monitor_interval: int,
        producer: PersonProducer,
        generator: PersonGenerator,
        shutdown_event: threading.Event
    ):
        """
        Initialize the queue monitor.

        Args:
            host: RabbitMQ server hostname
            port: RabbitMQ server port
            user: RabbitMQ username
            password: RabbitMQ password
            queue_name: Queue name to monitor
            min_queue_size: Minimum number of messages to maintain
            monitor_interval: Seconds between checks
            producer: PersonProducer instance for sending records
            generator: PersonGenerator instance for creating records
            shutdown_event: Threading event to signal shutdown
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.queue_name = queue_name
        self.min_queue_size = min_queue_size
        self.monitor_interval = monitor_interval
        self.producer = producer
        self.generator = generator
        self.shutdown_event = shutdown_event
        self.logger = logging.getLogger("name-provider.monitor")

    def run(self):
        """
        Main monitoring loop. Runs until shutdown_event is set.

        Checks queue depth at regular intervals and produces records
        when below threshold.
        """
        self.logger.info(
            f"Monitor started: checking every {self.monitor_interval}s, "
            f"maintaining minimum {self.min_queue_size} messages"
        )

        while not self.shutdown_event.is_set():
            try:
                available = self._get_queue_message_count()

                if available < self.min_queue_size:
                    needed = self.min_queue_size - available
                    self._produce_batch(needed)
                    self.logger.info(
                        f"Produced {needed} records (was {available}, now ~{self.min_queue_size})"
                    )
                else:
                    self.logger.debug(f"Queue healthy: {available} messages available")

            except Exception as e:
                self.logger.error(f"Monitor error: {e}", exc_info=True)

            # Wait for next check (or shutdown signal)
            self.shutdown_event.wait(self.monitor_interval)

        self.logger.info("Monitor stopped")

    def _get_queue_message_count(self) -> int:
        """
        Get the number of ready messages in the queue.

        Returns:
            int: Number of messages ready for consumption
        """
        try:
            # Create connection to check queue
            credentials = pika.PlainCredentials(self.user, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials
            )

            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()

            # Declare queue (passive=True means don't create, just check)
            # Returns method frame with message_count
            method_frame = channel.queue_declare(
                queue=self.queue_name,
                durable=True,
                passive=False  # Create if doesn't exist
            )

            message_count = method_frame.method.message_count

            connection.close()

            self.logger.debug(f"Queue has {message_count} messages")
            return message_count

        except Exception as e:
            self.logger.error(f"Error checking queue depth: {e}")
            return 0  # Assume empty on error, will retry

    def _produce_batch(self, count: int):
        """
        Produce a batch of person records.

        Args:
            count: Number of records to produce
        """
        success_count = 0
        for i in range(count):
            person = self.generator.generate_person()
            if self.producer.send(person):
                success_count += 1

        if success_count < count:
            self.logger.warning(
                f"Only {success_count}/{count} records sent successfully"
            )
