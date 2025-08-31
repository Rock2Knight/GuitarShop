import json
from typing import Any, Optional
from datetime import datetime

from loguru import logger
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis.asyncio import Redis

from app.config import settings

class RedisCache:
    _instance = None
    _redis: Redis = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance


    async def init_redis(self):
        if not self._initialized:
            self._redis = Redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=False,  # Важно для бинарных данных
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                max_connections=10
            )
            try:
                await self._redis.ping()
                FastAPICache.init(RedisBackend(self._redis), prefix="fastapi-cache")
                self._initialized = True
                logger.info("Redis connection established")
            except Exception as e:
                logger.error(f"Redis connection failed: {e}")
                raise
        return self._redis


    async def get(self, key: str) -> Any:
        try:
            data = await self._redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None


    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        try:
            if ttl is None:
                ttl = settings.CACHE_TTL
            serialized = json.dumps(value, default=self._json_serializer)
            return await self._redis.setex(key, ttl, serialized)
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False


    async def delete(self, key: str) -> bool:
        """Удалить данные по ключу (общий метод)"""
        try:
            deleted = await self._redis.delete(key)
            return deleted == 1
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False


    def _json_serializer(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    async def close(self):
        if self._redis:
            await self._redis.close()


cache = RedisCache()