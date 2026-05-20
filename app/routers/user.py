from fastapi import APIRouter, Response, status, HTTPException, Depends
from loguru import logger

from app.cache.redis import RedisCache
from app.access.base_access import access_model
from app.access.user import access_user
from app.dependencies.cache import get_cache
from app.dto.user import UserDto
from app.loaders.user import UserLoader
from auth_service.auth import get_current_user

user_router = APIRouter(prefix="/user", tags=["Пользователи"])

@user_router.get("/{id}")
async def get_user(
    id: int,
    cache: RedisCache = Depends(get_cache),
    user_id = Depends(get_current_user)
):
    cache_key = f"user:{id}"
    
    # Проверка кэша с логированием
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.info(f"Cache HIT for key {cache_key}")
        return cached_data

    logger.info(f"Cache MISS for key {cache_key}")

    user_dump = {'method': 'get', 'id': id}
    user_resp = await access_user(**user_dump)
    
    if isinstance(user_resp, dict):
        # Сохранение в кэш с проверкой
        success = await cache.set(cache_key, user_resp)
        if not success:
            logger.error(f"Failed to cache data for key {cache_key}")
        #response.status_code = status.HTTP_200_OK
        return user_resp
    else:
        #response.status_code = 500
        return user_resp     # Если возникла ошибка


@user_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user_dto: UserDto.Create, user_id = Depends(get_current_user)):

    user_dump = {'method': 'post', 'dto': user_dto.model_dump()}
    return await access_user(**user_dump)


@user_router.patch("/{id}")
async def patch_user(
    id: int, user_dto: UserDto.Update, 
    response: Response,
    user_id = Depends(get_current_user)
):

    user_dump = {'method': 'patch', 'id': id, 'dto': user_dto.model_dump()}
    user_resp = await access_user(**user_dump)
    if isinstance(user_resp, HTTPException):
        response.status_code = user_resp.status_code
        return HTTPException(status_code=user_resp.status_code)
    response.status_code = status.HTTP_201_CREATED
    return user_resp
    

@user_router.delete("/{id}")
async def delete_user(id: int, response: Response, user_id = Depends(get_current_user)):

    user_dump = {'method': 'delete', 'id': id}
    user_resp = await access_model(loader_class=UserLoader, **user_dump)
    if isinstance(user_resp, HTTPException):
        response.status_code = user_resp.status_code
    return user_resp     # Если возникла ошибка