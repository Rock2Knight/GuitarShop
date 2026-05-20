from datetime import datetime

from fastapi import APIRouter, Response, status, HTTPException, Depends
from fastapi.responses import JSONResponse
from loguru import logger

from app.cache.redis import RedisCache
from app.access.base_access import access_model
from app.dependencies.cache import get_cache
from app.dto.effect import EffectPedalDto
from app.loaders.effect import EffectLoader
from app.auth_service.auth import get_current_user

effect_router = APIRouter(prefix="/effect", tags=["Педали эффектов"])

@effect_router.get("/{id}")
async def get_effect(
    id: int,
    cache: RedisCache = Depends(get_cache),
    user_id = Depends(get_current_user)
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

        effect_resp["created_at"] = datetime.isoformat(effect_resp["created_at"])
        effect_resp["updated_at"] = datetime.isoformat(effect_resp["updated_at"])
        return JSONResponse(
            content=effect_resp,
            status_code=status.HTTP_200_OK
        )
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return effect_resp     # Если возникла ошибка


@effect_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_effect(
    effect_dto: EffectPedalDto.Create,
    user_id = Depends(get_current_user)
):

    effect_dump = {'method': 'post', 'dto': effect_dto.model_dump()}
    access_resp = await access_model(
        loader_class=EffectLoader,
        **effect_dump
    )

    access_resp["created_at"] = datetime.isoformat(access_resp["created_at"])
    access_resp["updated_at"] = datetime.isoformat(access_resp["updated_at"])

    if access_resp and isinstance(access_resp, dict):
        return JSONResponse(
            content=access_resp,
            status_code=status.HTTP_201_CREATED
        )


@effect_router.patch("/{id}")
async def patch_effect(
    id: int, 
    effect_dto: EffectPedalDto.Update, 
    response: Response,
    cache: RedisCache = Depends(get_cache),
    user_id = Depends(get_current_user)
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
async def delete_effect(
    id: int, response: Response, 
    user_id = Depends(get_current_user)
):

    effect_dump = {'method': 'delete', 'id': id}
    effect_resp = await access_model(
        loader_class=EffectLoader,
        **effect_dump
    )
    if isinstance(effect_resp, HTTPException):
        response.status_code = effect_resp.status_code
    return effect_resp     # Если возникла ошибка