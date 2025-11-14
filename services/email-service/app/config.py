"""Configuration settings"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Service
    service_name: str = "email-service"
    service_version: str = "1.0.0"
    port: int = 3005
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    # RabbitMQ
    rabbitmq_url: str = "amqp://admin:admin123@rabbitmq:5672/"
    
    # Template Service
    template_service_url: str = "http://template-service:3004"
    
    # Worker
    worker_enabled: bool = True
    worker_prefetch_count: int = 10
    
    # Mock Mode
    mock_mode: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
