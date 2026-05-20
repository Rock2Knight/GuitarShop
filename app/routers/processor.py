from fastapi import APIRouter, Response, status, HTTPException, Depends
from loguru import logger

from app.cache.redis import RedisCache
from app.access.base_access import access_model
from app.auth_service.auth import get_current_user
from app.dependencies.cache import get_cache
from app.dto.processor import ProcessorDto
from app.loaders.processor import ProcessorLoader

processor_router = APIRouter(prefix="/processor", tags=["Гитарные процессоры"])

@processor_router.get("/{id}")
async def get_processor(
    id: int, 
    cache: RedisCache = Depends(get_cache),
    user_id = Depends(get_current_user)
):
    cache_key = f"processor:{id}"

    # Проверка кэша с логированием
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.info(f"Cache HIT for key {cache_key}")
        return cached_data

    logger.info(f"Cache MISS for key {cache_key}")

    processor_dump = {'method': 'get', 'id': id}
    processor_resp = await access_model(
        loader_class=ProcessorLoader,
        **processor_dump
    )
    
    if isinstance(processor_resp, dict):
        # Сохранение в кэш с проверкой
        success = await cache.set(cache_key, processor_resp)
        if not success:
            logger.error(f"Failed to cache data for key {cache_key}")
        return processor_resp
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return processor_resp     # Если возникла ошибка


@processor_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_processor(
    processor_dto: ProcessorDto.Create,
    user_id = Depends(get_current_user)
):

    processor_dump = {'method': 'post', 'dto': processor_dto.model_dump()}
    return await access_model(
        loader_class=ProcessorLoader,
        **processor_dump
    )


@processor_router.patch("/{id}")
async def patch_processor(
    id: int, processor_dto: ProcessorDto.Update, 
    response: Response,
    user_id = Depends(get_current_user)
):

    processor_dump = {'method': 'patch', 'id': id, 'dto': processor_dto.model_dump()}
    processor_resp = await access_model(
        loader_class=ProcessorLoader,
        **processor_dump
    )
    if isinstance(processor_resp, HTTPException):
        if processor_resp.status_code > 500:
            raise HTTPException(status_code=500, detail=processor_resp.detail)
    response.status_code = status.HTTP_201_CREATED
    return processor_resp
    

@processor_router.delete("/{id}")
async def delete_processor(
    id: int, response: Response,
    user_id = Depends(get_current_user)
):

    processor_dump = {'method': 'delete', 'id': id}
    processor_resp = await access_model(
        loader_class=ProcessorLoader, 
        **processor_dump
    )
    if isinstance(processor_resp, HTTPException):
        if processor_resp.status_code > 500:
            raise HTTPException(status_code=500, detail=processor_resp.detail)
    return processor_resp     # Если возникла ошибка