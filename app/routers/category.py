from fastapi import APIRouter, Response, status, HTTPException, Depends
from loguru import logger

from app.cache.redis import RedisCache
from app.auth_service.auth import get_current_user
from app.dependencies.cache import get_cache
from app.access.category import access_category
from app.dto.category import CategoryDto

category_router = APIRouter(prefix="/category", tags=["Категории"])

@category_router.get("/{name}")
async def get_category(
    name: str,
    cache: RedisCache = Depends(get_cache),
    user_id = Depends(get_current_user)
):
    cache_key = f"category:{name}"
    
    # Проверка кэша с логированием
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.info(f"Cache HIT for key {cache_key}")
        return cached_data

    logger.info(f"Cache MISS for key {cache_key}")
    
    # Получение данных из БД
    category_resp = await access_category(
        method='get',
        name=name
    )
    
    if isinstance(category_resp, dict):
        # Сохранение в кэш с проверкой
        success = await cache.set(cache_key, category_resp)
        if not success:
            logger.error(f"Failed to cache data for key {cache_key}")
        return category_resp
    else:
        raise HTTPException(status_code=500, detail=category_resp.detail)


@category_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_category(
    category_dto: CategoryDto.Create,
    user_id = Depends(get_current_user)
):

    category_dump = {'method': 'post', 'dto': category_dto.model_dump()}
    return await access_category(
        **category_dump
    )


@category_router.patch("/{id}")
async def patch_category(
    id: int, 
    category_dto: CategoryDto.Update, 
    response: Response,
    cache: RedisCache = Depends(get_cache),
    user_id = Depends(get_current_user)
):
    await cache.delete(f"category:{id}")

    category_dump = {'method': 'patch', 'id': id, 'dto': category_dto.model_dump()}
    category_resp = await access_category(
        **category_dump
    )
    if isinstance(category_resp, HTTPException):
        response.status_code = category_resp.status_code
        raise HTTPException(status_code=category_resp.status_code, detail=category_resp.detail)
    response.status_code = status.HTTP_201_CREATED
    return category_resp
    

@category_router.delete("/{id}")
async def delete_category(
    id: int, response: Response,
    user_id = Depends(get_current_user)
):

    category_dump = {'method': 'delete', 'id': id}
    category_resp = await access_category(
        **category_dump
    )
    if isinstance(category_resp, HTTPException):
        response.status_code = category_resp.status_code
    return category_resp     # Если возникла ошибка