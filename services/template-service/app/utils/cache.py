"""
Redis caching utilities
"""

import redis
import json
import logging
from typing import Optional, Any
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class CacheClient:
    """Redis cache client"""
    
    def __init__(self):
        self.client = None
        self._connect()
    
    def _connect(self):
        """Connect to Redis"""
        try:
            redis_url = getattr(settings, 'redis_url', None)
            if redis_url:
                self.client = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                # Test connection
                self.client.ping()
                logger.info("✅ Connected to Redis")
            else:
                logger.warning("⚠️ Redis URL not configured, caching disabled")
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {str(e)}, caching disabled")
            self.client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.client:
            return None
        
        try:
            value = self.client.get(key)
            if value:
                logger.debug(f"Cache HIT: {key}")
                return json.loads(value)
            logger.debug(f"Cache MISS: {key}")
            return None
        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache with TTL"""
        if not self.client:
            return False
        
        try:
            self.client.setex(
                key,
                ttl,
                json.dumps(value, default=str)
            )
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.client:
            return False
        
        try:
            self.client.delete(key)
            logger.debug(f"Cache DELETE: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {str(e)}")
            return False
    
    def delete_pattern(self, pattern: str) -> bool:
        """Delete all keys matching pattern"""
        if not self.client:
            return False
        
        try:
            keys = self.client.keys(pattern)
            if keys:
                self.client.delete(*keys)
                logger.debug(f"Cache DELETE pattern: {pattern} ({len(keys)} keys)")
            return True
        except Exception as e:
            logger.error(f"Cache delete pattern error: {str(e)}")
            return False


# Global cache client
cache_client = CacheClient()


def get_cache_client() -> CacheClient:
    """Get cache client"""
    return cache_client