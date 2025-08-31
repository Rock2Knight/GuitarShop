from fastapi import APIRouter, Response, status, HTTPException, Depends
from loguru import logger

from app.cache.redis import RedisCache
from app.access.base_access import access_model
from app.dependencies.cache import get_cache
from app.dto.effect import EffectPedalDto
from app.loaders.effect import EffectLoader

effect_router = APIRouter(prefix="/effect", tags=["Педали эффектов"])

@effect_router.get("/{id}")
async def get_effect(
    id: int,
    cache: RedisCache = Depends(get_cache)
):
    cache_key = f"effect:{id}"
    
    # Проверка кэша с логированием
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.info(f"Cache HIT for key {cache_key}")
        return cached_data

    logger.info(f"Cache MISS for key {cache_key}")
    
    effect_dump = {'method': 'get', 'id': id}
    effect_resp = await access_model(
        loader_class=EffectLoader,
        **effect_dump
    )
    
    if isinstance(effect_resp, dict):
        # Сохранение в кэш с проверкой
        success = await cache.set(cache_key, effect_resp)
        if not success:
            logger.error(f"Failed to cache data for key {cache_key}")
        return effect_resp
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return effect_resp     # Если возникла ошибка


@effect_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_effect(processor_dto: EffectPedalDto.Create):

    effect_dump = {'method': 'post', 'dto': processor_dto.model_dump()}
    return await access_model(
        loader_class=EffectLoader,
        **effect_dump
    )


@effect_router.patch("/{id}")
async def patch_effect(
    id: int, 
    effect_dto: EffectPedalDto.Update, 
    response: Response,
    cache: RedisCache = Depends(get_cache)
):
    await cache.delete(f"effect:{id}")

    effect_dump = {'method': 'patch', 'id': id, 'dto': effect_dto.model_dump()}
    effect_resp = await access_model(
        loader_class=EffectLoader,
        **effect_dump
    )
    if isinstance(effect_resp, HTTPException):
        response.status_code = effect_resp.status_code
        return HTTPException(status_code=effect_resp.status_code)
    response.status_code = status.HTTP_201_CREATED
    return effect_resp
    

@effect_router.delete("/{id}")
async def delete_effect(id: int, response: Response):

    effect_dump = {'method': 'delete', 'id': id}
    effect_resp = await access_model(
        loader_class=EffectLoader,
        **effect_dump
    )
    if isinstance(effect_resp, HTTPException):
        response.status_code = effect_resp.status_code
    return effect_resp     # Если возникла ошибка