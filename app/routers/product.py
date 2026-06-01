from fastapi import APIRouter, Response, status, HTTPException, Depends
from loguru import logger

from app.cache.redis import RedisCache
from app.access.base_access import access_model
from app.auth_service.auth import get_current_user
from app.dependencies.cache import get_cache
from app.dto.guitar import GuitarDto
from app.loaders.product import ProductLoader

product_router = APIRouter(prefix="/product", tags=["Гитары"])

@product_router.get("/{id}")
async def get_product(
    id: int,
    cache: RedisCache = Depends(get_cache),
    user_id = Depends(get_current_user)
):
    cache_key = f"product:{id}"
    
    # Проверка кэша с логированием
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.info(f"Cache HIT for key {cache_key}")
        return cached_data

    logger.info(f"Cache MISS for key {cache_key}")
    
    # Получение данных из БД
    product_resp = await access_model(
        loader_class=ProductLoader,
        method='get',
        id=id
    )
    
    if isinstance(product_resp, dict):
        # Сохранение в кэш с проверкой
        success = await cache.set(cache_key, product_resp)
        if not success:
            logger.error(f"Failed to cache data for key {cache_key}")
        return product_resp
    else:
        raise HTTPException(status_code=500, detail=product_resp.detail)


@product_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product(
    product_dto: GuitarDto.Create,
    user_id = Depends(get_current_user)
):

    product_dump = {'method': 'post', 'dto': product_dto.model_dump()}
    return await access_model(
        loader_class=ProductLoader,
        **product_dump
    )


@product_router.patch("/{id}")
async def patch_product(
    id: int, 
    product_dto: GuitarDto.Update, 
    response: Response,
    cache: RedisCache = Depends(get_cache),
    user_id = Depends(get_current_user)
):
    await cache.delete(f"product:{id}")

    product_dump = {'method': 'patch', 'id': id, 'dto': product_dto.model_dump()}
    product_resp = await access_model(
        loader_class=ProductLoader,
        **product_dump
    )
    if isinstance(product_resp, HTTPException):
        response.status_code = product_resp.status_code
        raise HTTPException(status_code=product_resp.status_code, detail=product_resp.detail)
    response.status_code = status.HTTP_201_CREATED
    return product_resp
    

@product_router.delete("/{id}")
async def delete_product(
    id: int, response: Response,
    user_id = Depends(get_current_user)
):

    product_dump = {'method': 'delete', 'id': id}
    product_resp = await access_model(
        loader_class=ProductLoader,
        **product_dump
    )
    if isinstance(product_resp, HTTPException):
        response.status_code = product_resp.status_code
    return product_resp     # Если возникла ошибка