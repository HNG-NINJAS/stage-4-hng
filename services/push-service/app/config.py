from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # Service
    service_name: str = "push-service"
    service_version: str = "1.0.0"
    port: int = 3003
    
    # Environment
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    # RabbitMQ
    rabbitmq_url: str = "amqp://admin:admin123@rabbitmq:5672/"
    push_queue_name: str = "push.queue"
    
    # Template Service
    template_service_url: str = "http://template-service:3004"
    
    # Firebase FCM
    fcm_credentials_path: Optional[str] = None  # Path to service account JSON
    fcm_project_id: Optional[str] = None
    
    # Redis (optional - for caching tokens)
    redis_url: Optional[str] = "redis://:redis123@redis:6379/1"
    
    # Worker
    worker_enabled: bool = True
    worker_prefetch_count: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()