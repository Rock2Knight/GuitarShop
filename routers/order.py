from fastapi import APIRouter, Response, status, HTTPException
from access.order import access_order
from dto.order import OrderDto
from loaders.order import OrderLoader

order_router = APIRouter(prefix="/order", tags=["Заказы"])

@order_router.get("/{id}")
async def get_order(id: int, response: Response):

    order_dump = {'method': 'get', 'id': id}
    order_resp = await access_order(**order_dump)
    
    if isinstance(order_resp, dict):
        return order_resp
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
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