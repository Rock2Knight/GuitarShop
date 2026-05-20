from loguru import logger

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.cache.redis import cache
from app.auth_service.token_storage import TokenStorage

security = HTTPBearer()
token_storage = TokenStorage(cache)  # cache из вашего кода

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    token = credentials.credentials
    logger.info(f"Bearer token = {token}")
    
    data = await cache.get(f"token:access:{token}")
    if data:
        logger.info(f"Redis data: {data}")
    else:
        logger.info("No data in Redis")
    # ВАЖНО: определяем тип токена по формату или из БД
    # Простой вариант: access токены начинаются с "a_", refresh с "r_"
    #token_type = "access" if token.startswith("a_") else "refresh"
    
    #token_data = await token_storage.validate_token(token, token_type)
    if not data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return data.get("user_id")