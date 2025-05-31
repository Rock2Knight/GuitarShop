from typing import Optional

from fastapi import HTTPException, status

from access.base_access import access_model
from loaders.order import OrderLoader
from models import Order

async def access_order(**kwargs) -> Optional[Order | HTTPException]:
    match kwargs['method']:
        case "get":
            order = await access_model(**kwargs)
            return await order.to_dict()
        case "post":
            try:
                order = await OrderLoader.create(user_id=kwargs['user_id'])
                return await order.to_dict()
            except Exception:
                return HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        case 'patch':
            order = await access_model(**kwargs)
            return await order.to_dict()
        case "delete":
            try:
                return await OrderLoader.delete(order_id=kwargs['id'])
            except Exception:
                return HTTPException(status_code=status.HTTP_400_BAD_REQUEST)