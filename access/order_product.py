from typing import Optional

from fastapi import HTTPException, status

from access.base_access import access_model
from loaders.order_product import OrderProductLoader
from models import OrderProduct

async def access_order_product(**kwargs) -> Optional[OrderProduct | HTTPException]:
    if kwargs['method'] == 'post':
        try:
            order_product = await OrderProductLoader.create(**kwargs['dto'])
            return await order_product.to_dict()
        except Exception:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    else:
        return await access_model(loader_class=OrderProduct, **kwargs)