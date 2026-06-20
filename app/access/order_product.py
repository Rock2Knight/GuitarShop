from typing import Optional

from fastapi import HTTPException, status

from app.loaders.order_product import OrderProductLoader
from app.loaders.cart_product import CartProductLoader
from app.loaders.product import ProductLoader
from app.models import OrderProduct

async def access_order_product(**kwargs) -> Optional[OrderProduct | HTTPException]:
    if kwargs['method'] == 'get':
        try:
            order_product = await OrderProductLoader.get(item_id=kwargs["id"])
            if not order_product:
                return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This product hasn't been added to cart")

            order_product_info = await order_product.to_dict()
            product = await ProductLoader.get(item_id=order_product.product_id)
            order_product_info["product_name"] = product.name
            return order_product_info
        except Exception as e:
            return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    elif kwargs['method'] == 'post':
        try:
            cart_product = await CartProductLoader.get(item_id=kwargs['dto']['cart_product_id'])
            if not cart_product:
                return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product with such id hasn't been reserved")

            kwargs['dto']['price_at_time'] = cart_product.price_at_time
            kwargs['dto']['quantity'] = cart_product.quantity
            kwargs['dto']['product_id'] = cart_product.product_id

            kwargs['dto'].pop('cart_product_id')
            order_product = await OrderProductLoader.create(**kwargs['dto'])
            order_product_info = await order_product.to_dict()
        
            await CartProductLoader.delete(item_id=cart_product.id)
            product = await ProductLoader.get(item_id=order_product.product_id)
            order_product_info["product_name"] = product.name
            return order_product_info
        except Exception as e:
            return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    elif kwargs['method'] == 'delete':
        try:
            order_product = await OrderProductLoader.delete(item_id=kwargs["id"])
            product = await ProductLoader.get(item_id=order_product["product_id"])
            order_product["product_name"] = product.name
            return order_product
        except Exception as e:
            return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))