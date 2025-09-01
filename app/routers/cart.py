from fastapi import APIRouter, Response, status, HTTPException, Depends
from loguru import logger

from app.cache.redis import RedisCache
from app.access.base_access import access_model
from app.dependencies.cache import get_cache
from app.dto.cart_product import CartProductDto
from app.loaders.cart_product import CartProductLoader

cart_product_router = APIRouter(prefix="/cart_product", tags=["Элементы корзины"])

@cart_product_router.get("/{id}")
async def get_cart_product(
    id: int, 
    cache: RedisCache = Depends(get_cache)
):
    cache_key = f"cart_product:{id}"
    
    # Проверка кэша с логированием
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.info(f"Cache HIT for key {cache_key}")
        return cached_data

    logger.info(f"Cache MISS for key {cache_key}")
    
    cart_product_dump = {'method': 'get', 'id': id}
    cart_product_resp = await access_model(loader_class=CartProductLoader, **cart_product_dump)
    
    if isinstance(cart_product_resp, dict):
        # Сохранение в кэш с проверкой
        success = await cache.set(cache_key, cart_product_resp)
        if not success:
            logger.error(f"Failed to cache data for key {cache_key}")
        #response.status_code = status.HTTP_200_OK
        return cart_product_resp
    else:
        #response.status_code = status.HTTP_404_NOT_FOUND
        return cart_product_resp     # Если возникла ошибка


@cart_product_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_cart_product(cart_product_dto: CartProductDto.Create):

    cart_product_dump = {'method': 'post', 'dto': cart_product_dto.model_dump()}
    return await access_model(loader_class=CartProductLoader, **cart_product_dump)


@cart_product_router.patch("/{id}")
async def patch_cart_product(id: int, cart_product_dto: CartProductDto.Update, response: Response):

    cart_product_dump = {'method': 'patch', 'id': id, 'dto': cart_product_dto.model_dump()}
    cart_product_resp = await access_model(loader_class=CartProductLoader, **cart_product_dump)
    if isinstance(cart_product_resp, HTTPException):
        response.status_code = cart_product_resp.status_code
        return HTTPException(status_code=cart_product_resp.status_code)
    response.status_code = status.HTTP_201_CREATED
    return cart_product_resp
    

@cart_product_router.delete("/{id}")
async def delete_cart_product(id: int, response: Response):

    cart_product_dump = {'method': 'delete', 'id': id}
    cart_product_resp = await access_model(loader_class=CartProductLoader, **cart_product_dump)
    if isinstance(cart_product_resp, HTTPException):
        response.status_code = cart_product_resp.status_code
    return cart_product_resp     # Если возникла ошибка