"""
Utility functions for logging and helper operations.
"""
import logging
import time
import pika


def setup_logging(log_level: str) -> logging.Logger:
    """
    Configure structured logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        logging.Logger: Configured logger instance
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger("name-provider")


def wait_for_rabbitmq(host: str, port: int, user: str, password: str,
                       max_retries: int = 12, retry_delay: int = 5) -> bool:
    """
    Wait for RabbitMQ to be ready by attempting to create a connection.

    Args:
        host: RabbitMQ server hostname
        port: RabbitMQ server port
        user: RabbitMQ username
        password: RabbitMQ password
        max_retries: Maximum number of connection attempts
        retry_delay: Seconds to wait between retries

    Returns:
        bool: True if RabbitMQ is ready, False if max retries exceeded
    """
    logger = logging.getLogger("name-provider")
    logger.info(f"Waiting for RabbitMQ at {host}:{port}...")

    for attempt in range(1, max_retries + 1):
        try:
            # Try to create a connection to test
            credentials = pika.PlainCredentials(user, password)
            parameters = pika.ConnectionParameters(
                host=host,
                port=port,
                credentials=credentials,
                connection_attempts=1,
                retry_delay=1
            )
            connection = pika.BlockingConnection(parameters)
            connection.close()
            logger.info(f"RabbitMQ is ready (attempt {attempt}/{max_retries})")
            return True
        except pika.exceptions.AMQPConnectionError:
            if attempt < max_retries:
                logger.warning(f"RabbitMQ not ready, retrying in {retry_delay}s... (attempt {attempt}/{max_retries})")
                time.sleep(retry_delay)
            else:
                logger.error(f"RabbitMQ not available after {max_retries} attempts")
                return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to RabbitMQ: {e}")
            return False

    return False
