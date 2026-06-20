from typing import Optional

from fastapi import HTTPException, status

from app.loaders.product import ProductLoader
from app.loaders.cart_product import CartProductLoader
from app.models import CartProduct

async def access_cart_product(**kwargs) -> Optional[CartProduct | HTTPException]:
    if kwargs['method'] == 'get':
        try:
            cart_product = await CartProductLoader.get(item_id=kwargs["id"])
            if not cart_product:
                return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This product hasn't been added to cart")

            product = await ProductLoader.get(item_id=cart_product.product_id)

            cart_product_info = await cart_product.to_dict()
            cart_product_info["product_name"] = product.name
            return cart_product_info
        except Exception as e:
            return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    elif kwargs['method'] == 'post':
        try:
            product = await ProductLoader.get(item_id=kwargs['dto']['product_id'])
            if not product:
                return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product with such id not found")

            kwargs['dto']['price_at_time'] = product.price

            cart_product = await CartProductLoader.create(**kwargs['dto'])
            cart_product_info = await cart_product.to_dict()
            cart_product_info["product_name"] = product.name
            return cart_product_info
        except Exception as e:
            return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    elif kwargs['method'] == 'patch':
        try:
            # TODO добавить получение цены товара
            cart_product = await CartProductLoader.get(item_id=kwargs['id'])
            if not cart_product:
                return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This product hasn't been added to cart")

            product = await ProductLoader.get(item_id=cart_product.product_id)
            if not product:
                return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product with such id not found")
            kwargs['dto']['price_at_time'] = product.price

            cart_product = await CartProductLoader.update(item_id=kwargs['id'], **kwargs['dto'])
            cart_product_info = await cart_product.to_dict()
            cart_product_info["product_name"] = product.name
            return cart_product_info
        except Exception as e:
            return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    elif kwargs['method'] == 'delete':
        try:
            cart_product = await CartProductLoader.delete(item_id=kwargs["id"])
            if not cart_product:
                return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This product hasn't been added to cart")
            product = await ProductLoader.get(item_id=cart_product["product_id"])
            cart_product["product_name"] = product.name
            return cart_product
        except Exception as e:
            return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    