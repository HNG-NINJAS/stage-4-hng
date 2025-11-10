"""
Configuration management using Pydantic Settings
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_url: str
    
    # Redis
    redis_url: Optional[str] = None
    
    # RabbitMQ
    rabbitmq_url: Optional[str] = "amqp://admin:admin123@localhost:5672/"
    
    # Service
    service_name: str = "template-service"
    service_version: str = "1.0.0"
    port: int = 3004
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # Logging
    log_level: str = "INFO"
    
    # API
    api_prefix: str = "/api/v1"
    
    # CORS
    cors_origins: list = ["*"]
    
    # Cache TTL (seconds)
    cache_ttl: int = 300  # 5 minutes
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()