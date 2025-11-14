"""Cache middleware for API responses."""

import json
import hashlib
from typing import Any, Optional, Callable
from functools import wraps

from redis import Redis
from fastapi import Request

from app.core.config import settings


class CacheManager:
    """Manages caching operations."""

    def __init__(self):
        """Initialize cache manager."""
        self.redis_client: Optional[Redis] = None
        self._connect()

    def _connect(self):
        """Connect to Redis."""
        try:
            if settings.redis_url:
                self.redis_client = Redis.from_url(
                    settings.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                )
                self.redis_client.ping()
            else:
                self.redis_client = None
        except Exception:
            self.redis_client = None

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key."""
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        return f"cache:{hashlib.md5(key_data.encode()).hexdigest()}"

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.redis_client:
            return None
        try:
            value = self.redis_client.get(key)
            return json.loads(value) if value else None
        except Exception:
            return None

    def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in cache."""
        if not self.redis_client:
            return
        try:
            self.redis_client.setex(key, ttl, json.dumps(value))
        except Exception:
            pass

    def delete(self, key: str):
        """Delete key from cache."""
        if not self.redis_client:
            return
        try:
            self.redis_client.delete(key)
        except Exception:
            pass

    def delete_pattern(self, pattern: str):
        """Delete keys matching pattern."""
        if not self.redis_client:
            return
        try:
            keys = self.redis_client.keys(f"cache:*{pattern}*")
            if keys:
                self.redis_client.delete(*keys)
        except Exception:
            pass


cache_manager = CacheManager()


def cached(ttl: int = 300, key_prefix: str = ""):
    """Cache decorator for functions."""

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = cache_manager._generate_key(
                key_prefix or func.__name__, *args, **kwargs
            )
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                return cached_value

            result = await func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            return result

        return wrapper

    return decorator


def invalidate_cache(pattern: str):
    """Invalidate cache by pattern."""
    cache_manager.delete_pattern(pattern)
