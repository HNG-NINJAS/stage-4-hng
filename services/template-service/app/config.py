"""
Configuration management using Pydantic Settings
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from functools import lru_cache
from typing import Optional, List, Union


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )
    
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
    cors_origins: Union[List[str], str] = ["*"]
    
    # Cache TTL (seconds)
    cache_ttl: int = 300  # 5 minutes
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            # Handle comma-separated string or single value
            if ',' in v:
                return [origin.strip() for origin in v.split(',')]
            return [v.strip()]
        return v


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()