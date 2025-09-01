from fastapi import APIRouter, Response, status, HTTPException, Depends
from loguru import logger

from app.cache.redis import RedisCache
from app.access.order_product import access_order_product
from app.dependencies.cache import get_cache
from app.dto.order_product import OrderProductDto

order_product_router = APIRouter(prefix="/order_product", tags=["Товары из заказа"])

@order_product_router.get("/{id}")
async def get_order_product(
    id: int, 
    cache: RedisCache = Depends(get_cache)
):
    cache_key = f"order_product:{id}"
    
    # Проверка кэша с логированием
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.info(f"Cache HIT for {cache_key}")
        return cached_data
    
    logger.info(f"Cache MISS for {cache_key}")
    
    order_product_dump = {'method': 'get', 'id': id}
    order_product_resp = await access_order_product(**order_product_dump)
    
    if isinstance(order_product_resp, dict):
        # Сохранение в кэш с проверкой
        success = await cache.set(cache_key, order_product_resp)
        if not success:
            logger.error(f"Failed to cache data for key {cache_key}")
        return order_product_resp
    else:
        return order_product_resp     # Если возникла ошибка


@order_product_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_order_product(order_product_dto: OrderProductDto.Create):

    order_product_dump = {'method': 'post', 'dto': order_product_dto.model_dump()}
    return await access_order_product(**order_product_dump)


@order_product_router.patch("/{id}")
async def patch_order_product(id: int, order_product_dto: OrderProductDto.Update, response: Response):

    order_product_dump = {'method': 'patch', 'id': id, 'dto': order_product_dto.model_dump()}
    order_product_resp = await access_order_product(**order_product_dump)
    if isinstance(order_product_resp, HTTPException):
        response.status_code = order_product_resp.status_code
        return HTTPException(status_code=order_product_resp.status_code)
    response.status_code = status.HTTP_201_CREATED
    return order_product_resp
    

@order_product_router.delete("/{id}")
async def delete_order_product(id: int, response: Response):

    order_product_dump = {'method': 'delete', 'id': id}
    order_product_resp = await access_order_product(**order_product_dump)
    if isinstance(order_product_resp, HTTPException):
        response.status_code = order_product_resp.status_code
    return order_product_resp     # Если возникла ошибка