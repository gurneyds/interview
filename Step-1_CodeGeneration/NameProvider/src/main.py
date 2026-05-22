"""
Main application entry point with lifecycle management.
"""
import sys
import signal
import threading
from .config import Config
from .utils import setup_logging, wait_for_rabbitmq
from .producer import PersonProducer
from .generator import PersonGenerator
from .monitor import QueueMonitor


class NameProviderApp:
    """
    Main application orchestrator for the NameProvider service.

    Manages initialization, signal handling, and graceful shutdown.
    """

    def __init__(self):
        """Initialize the application."""
        self.config = Config()
        self.logger = setup_logging(self.config.log_level)
        self.shutdown_event = threading.Event()
        self.producer = None
        self.monitor_thread = None

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """
        Handle shutdown signals (SIGTERM, SIGINT).

        Args:
            signum: Signal number
            frame: Current stack frame
        """
        signal_name = "SIGTERM" if signum == signal.SIGTERM else "SIGINT"
        self.logger.info(f"Received {signal_name}, initiating graceful shutdown...")
        self.shutdown_event.set()

    def run(self):
        """
        Main application run loop.

        Returns:
            int: Exit code (0 for success, 1 for error)
        """
        try:
            self.logger.info("NameProvider service starting...")
            self.logger.info(f"Configuration: {self.config.model_dump()}")

            # Wait for RabbitMQ to be ready
            if not wait_for_rabbitmq(
                host=self.config.rabbitmq_host,
                port=self.config.rabbitmq_port,
                user=self.config.rabbitmq_user,
                password=self.config.rabbitmq_password
            ):
                self.logger.error("Failed to connect to RabbitMQ, exiting")
                return 1

            # Initialize components
            self.producer = PersonProducer(
                host=self.config.rabbitmq_host,
                port=self.config.rabbitmq_port,
                user=self.config.rabbitmq_user,
                password=self.config.rabbitmq_password,
                queue_name=self.config.queue_name
            )

            generator = PersonGenerator()

            monitor = QueueMonitor(
                host=self.config.rabbitmq_host,
                port=self.config.rabbitmq_port,
                user=self.config.rabbitmq_user,
                password=self.config.rabbitmq_password,
                queue_name=self.config.queue_name,
                min_queue_size=self.config.min_queue_size,
                monitor_interval=self.config.monitor_interval_seconds,
                producer=self.producer,
                generator=generator,
                shutdown_event=self.shutdown_event
            )

            # Start monitor thread
            self.monitor_thread = threading.Thread(
                target=monitor.run,
                name="QueueMonitor",
                daemon=False  # Non-daemon for graceful shutdown
            )
            self.monitor_thread.start()

            self.logger.info("NameProvider service started successfully")

            # Wait for shutdown signal
            self.shutdown_event.wait()

            # Graceful shutdown
            self.logger.info("Waiting for monitor thread to finish...")
            self.monitor_thread.join(timeout=30)

            if self.producer:
                self.producer.close()

            self.logger.info("Shutdown complete")
            return 0

        except Exception as e:
            self.logger.error(f"Fatal error: {e}", exc_info=True)
            return 1


def main():
    """
    Application entry point.

    Returns:
        int: Exit code
    """
    app = NameProviderApp()
    exit_code = app.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
