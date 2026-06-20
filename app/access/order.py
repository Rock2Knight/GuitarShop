from typing import Optional

from fastapi import HTTPException, status

from app.access.base_access import access_model
from app.loaders.order import OrderLoader
from app.loaders.order_product import OrderProductLoader
from app.models import Order

async def access_order(**kwargs) -> Optional[Order | HTTPException]:
    match kwargs['method']:
        case "get":
            order_products = await OrderProductLoader.get_all_products_of_order(order_id=kwargs['id'])
            total_price = sum(product.price_at_time * product.quantity for product in order_products)
            order_products_info = [await product.to_dict() for product in order_products]
            order = await OrderLoader.get(item_id=kwargs['id'])
            order_info = await order.to_dict()
            order_info['total_price'] = total_price
            order_info['products'] = order_products_info
            return order_info

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