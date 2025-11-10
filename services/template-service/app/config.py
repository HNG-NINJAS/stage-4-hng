"""
Configuration management using Pydantic Settings
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )
    
    # Database
    database_url: str
    
    # Redis (optional)
    redis_url: Optional[str] = None
    
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


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()