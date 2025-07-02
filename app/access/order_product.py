from typing import Optional

from fastapi import HTTPException, status

from app.access.base_access import access_model
from app.loaders.order_product import OrderProductLoader
from app.models import OrderProduct

async def access_order_product(**kwargs) -> Optional[OrderProduct | HTTPException]:
    if kwargs['method'] == 'post':
        try:
            order_product = await OrderProductLoader.create(**kwargs['dto'])
            return await order_product.to_dict()
        except Exception as e:
            return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    else:
        return await access_model(loader_class=OrderProductLoader, **kwargs)