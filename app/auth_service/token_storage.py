from dataclasses import dataclass
from datetime import datetime, timedelta
import secrets

from redis.asyncio import Redis

from app.cache.redis import RedisCache

@dataclass
class TokenData:
    user_id: int
    token_type: str  # "access" или "refresh"
    expires_at: datetime


class TokenStorage:

    def __init__(self, redis_cache: RedisCache):
        self.cache = redis_cache


    def _make_key(self, token: str, token_type: str) -> str:
        return f"token:{token_type}:{token}"


    async def create_token(self, user_id: int, token_type: str, ttl_seconds: int) -> str:
        """Создаёт новый токен и сохраняет его в Redis"""
        token = secrets.token_urlsafe(32)  # случайный opaque-токен
        expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
        
        key = self._make_key(token, token_type)
        # сохраняем как словарь, а не JSON-строку
        await self.cache.set(key, {
            "user_id": user_id,
            "token_type": token_type,
            "expires_at": expires_at.isoformat()
        }, ttl=ttl_seconds)
        
        return token
    
    async def validate_token(self, token: str, token_type: str) -> TokenData:
        """Проверяет токен и возвращает данные"""
        key = self._make_key(token, token_type)
        data = await self.cache.get(key)
        
        if not data:
            return None
        
        # проверка срока действия (хотя Redis сам удалит по TTL)
        expires_at = datetime.fromisoformat(data["expires_at"])
        if expires_at < datetime.now():
            await self.cache.delete(key)
            return None
        
        return TokenData(
            user_id=data["user_id"],
            token_type=data["token_type"],
            expires_at=expires_at
        )
    
    async def revoke_token(self, token: str, token_type: str) -> bool:
        """Отзывает токен (logout)"""
        key = self._make_key(token, token_type)
        return await self.cache.delete(key)