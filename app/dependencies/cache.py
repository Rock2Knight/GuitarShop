from fastapi import Depends
from app.cache.redis import cache

async def get_cache():
    if not cache._initialized:
        await cache.init_redis()
    return cache