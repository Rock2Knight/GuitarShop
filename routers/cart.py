from fastapi import APIRouter, Response, status, HTTPException
from access.base_access import access_model
from dto.cart_product import CartProductDto
from loaders.cart_product import CartProductLoader

cart_product_router = APIRouter(prefix="/cart_product", tags=["Элементы корзины"])

@cart_product_router.get("/{id}")
async def get_cart_product(id: int, response: Response):

    cart_product_dump = {'method': 'get', 'id': id}
    cart_product_resp = await access_model(loader_class=CartProductLoader, **cart_product_dump)
    
    if isinstance(cart_product_resp, dict):
        return cart_product_resp
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
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