from fastapi import APIRouter, Response, status, HTTPException, Depends
from loguru import logger

from app.cache.redis import RedisCache
from app.access.base_access import access_model
from app.dependencies.cache import get_cache
from app.dto.guitar import GuitarDto
from app.loaders.guitar import GuitarLoader

guitar_router = APIRouter(prefix="/guitar", tags=["Гитары"])

@guitar_router.get("/{id}")
async def get_guitar(
    id: int,
    cache: RedisCache = Depends(get_cache)
):
    cache_key = f"guitar:{id}"
    
    # Проверка кэша с логированием
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.info(f"Cache HIT for key {cache_key}")
        return cached_data

    logger.info(f"Cache MISS for key {cache_key}")
    
    # Получение данных из БД
    guitar_resp = await access_model(
        loader_class=GuitarLoader,
        method='get',
        id=id
    )
    
    if isinstance(guitar_resp, dict):
        # Сохранение в кэш с проверкой
        success = await cache.set(cache_key, guitar_resp)
        if not success:
            logger.error(f"Failed to cache data for key {cache_key}")
        return guitar_resp
    else:
        raise HTTPException(status_code=500, detail=guitar_resp.detail)


@guitar_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_guitar(guitar_dto: GuitarDto.Create):

    guitar_dump = {'method': 'post', 'dto': guitar_dto.model_dump()}
    return await access_model(
        loader_class=GuitarLoader,
        **guitar_dump
    )


@guitar_router.patch("/{id}")
async def patch_guitar(
    id: int, 
    guitar_dto: GuitarDto.Update, 
    response: Response,
    cache: RedisCache = Depends(get_cache)
):
    await cache.delete(f"guitar:{id}")

    guitar_dump = {'method': 'patch', 'id': id, 'dto': guitar_dto.model_dump()}
    guitar_resp = await access_model(
        loader_class=GuitarLoader,
        **guitar_dump
    )
    if isinstance(guitar_resp, HTTPException):
        response.status_code = guitar_resp.status_code
        raise HTTPException(status_code=guitar_resp.status_code, detail=guitar_resp.detail)
    response.status_code = status.HTTP_201_CREATED
    return guitar_resp
    

@guitar_router.delete("/{id}")
async def delete_guitar(id: int, response: Response):

    guitar_dump = {'method': 'delete', 'id': id}
    guitar_resp = await access_model(
        loader_class=GuitarLoader,
        **guitar_dump
    )
    if isinstance(guitar_resp, HTTPException):
        response.status_code = guitar_resp.status_code
    return guitar_resp     # Если возникла ошибка