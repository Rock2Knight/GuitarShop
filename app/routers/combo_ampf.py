from fastapi import APIRouter, Response, status, HTTPException, Depends
from loguru import logger

from app.cache.redis import RedisCache
from app.access.base_access import access_model
from app.dependencies.cache import get_cache
from app.dto.combo_ampf import ComboAmpfDto
from app.loaders.combo_ampf import ComboAmpfLoader

combo_router = APIRouter(prefix="/combo_ampf", tags=["Комбо-усилители"])

@combo_router.get("/{id}")
async def get_combo(
    id: int, 
    cache: RedisCache = Depends(get_cache)
):
    cache_key = f"combo_ampf:{id}"

    # Проверка кэша с логированием
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.info(f"Cache HIT for key {cache_key}")
        return cached_data

    logger.info(f"Cache MISS for key {cache_key}")

    combo_dump = {'method': 'get', 'id': id}
    combo_resp = await access_model(
        loader_class=ComboAmpfLoader,
        **combo_dump
    )
    
    if isinstance(combo_resp, dict):
        # Сохранение в кэш с проверкой
        success = await cache.set(cache_key, guitar_resp)
        if not success:
            logger.error(f"Failed to cache data for key {cache_key}")
        return combo_resp
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return combo_resp     # Если возникла ошибка


@combo_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_combo(combo_dto: ComboAmpfDto.Create):

    combo_dump = {'method': 'post', 'dto': combo_dto.model_dump()}
    return await access_model(
        loader_class=ComboAmpfLoader,
        **combo_dump
    )


@combo_router.patch("/{id}")
async def patch_combo(
    id: int, 
    combo_dto: ComboAmpfDto.Update, 
    response: Response,
    cache: RedisCache = Depends(get_cache)
):
    await cache.delete(f"combo_ampf:{id}")

    combo_dump = {'method': 'patch', 'id': id, 'dto': combo_dto.model_dump()}
    combo_resp = await access_model(
        loader_class=ComboAmpfLoader,
        **combo_dump
    )
    if isinstance(combo_resp, HTTPException):
        response.status_code = combo_resp.status_code
        return HTTPException(status_code=combo_resp.status_code)
    response.status_code = status.HTTP_201_CREATED
    return combo_resp
    

@combo_router.delete("/{id}")
async def delete_combo(id: int, response: Response):

    combo_dump = {'method': 'delete', 'id': id}
    combo_resp = await access_model(
        loader_class=ComboAmpfLoader,
        **combo_dump
    )
    if isinstance(combo_resp, HTTPException):
        response.status_code = combo_resp.status_code
    return combo_resp     # Если возникла ошибка