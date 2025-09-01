from fastapi import APIRouter, Response, status, HTTPException, Depends
from loguru import logger

from app.cache.redis import RedisCache
from app.access.order import access_order
from app.dependencies.cache import get_cache
from app.dto.order import OrderDto
from app.loaders.order import OrderLoader

order_router = APIRouter(prefix="/order", tags=["Заказы"])

@order_router.get("/{id}")
async def get_order(
    id: int, 
    cache: RedisCache = Depends(get_cache)
):
    cache_key = f"order:{id}"
    
    # Проверка кэша с логированием
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.info(f"Cache HIT for {cache_key}")
        return cached_data
    
    logger.info(f"Cache MISS for {cache_key}")
    
    order_dump = {'method': 'get', 'id': id}
    order_resp = await access_order(**order_dump)
    
    if isinstance(order_resp, dict):
        # Сохранение в кэш с проверкой
        order_resp["order_date"] = order_resp["order_date"].strftime("%Y-%m-%d")
        success = await cache.set(cache_key, order_resp)
        if not success:
            logger.error(f"Failed to cache data for key {cache_key}")
        return order_resp
    else:
        #response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return order_resp     # Если возникла ошибка


@order_router.post("/{user_id}", status_code=status.HTTP_201_CREATED)
async def create_order(user_id: int):

    order_dump = {'method': 'post', 'user_id': user_id}
    return await access_order(**order_dump)


@order_router.patch("/{id}")
async def patch_order(id: int, order_dto: OrderDto, response: Response):

    order_dump = {'method': 'patch', 'id': id, 'dto': order_dto.model_dump()}
    order_resp = await access_order(**order_dump)
    if isinstance(order_resp, HTTPException):
        response.status_code = order_resp.status_code
        return HTTPException(status_code=order_resp.status_code)
    response.status_code = status.HTTP_201_CREATED
    return order_resp
    

@order_router.delete("/{id}")
async def delete_order(id: int, response: Response):

    order_dump = {'method': 'delete', 'id': id}
    order_resp = await access_order(**order_dump)
    if isinstance(order_resp, HTTPException):
        response.status_code = order_resp.status_code
    return order_resp     # Если возникла ошибка