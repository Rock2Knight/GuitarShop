from typing import Optional

from fastapi import HTTPException, status

from app.access.base_access import access_model
from app.loaders.order import OrderLoader
from app.models import Order

async def access_order(**kwargs) -> Optional[Order | HTTPException]:
    match kwargs['method']:
        case "get":
            return await access_model(loader_class=OrderLoader, **kwargs)
        case "post":
            try:
                order = await OrderLoader.create(user_id=kwargs['user_id'])
                return await order.to_dict()
            except Exception as e:
                raise e
        case 'patch':
            return await access_model(loader_class=OrderLoader, **kwargs)
        case "delete":
            try:
                return await OrderLoader.delete(order_id=kwargs['id'])
            except Exception as e:
                raise e