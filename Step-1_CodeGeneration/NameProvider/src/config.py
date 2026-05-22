"""
Configuration management using environment variables.
"""
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """
    Application configuration loaded from environment variables.

    All settings have sensible defaults for local development.
    Override via environment variables or .env file.
    """
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"
    queue_name: str = "genealogy-persons"
    min_queue_size: int = 10
    batch_production_size: int = 5
    monitor_interval_seconds: int = 5
    log_level: str = "INFO"

    model_config = {
        "env_file": ".env",
        "case_sensitive": False
    }
