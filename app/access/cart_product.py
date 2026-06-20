from typing import Optional

from fastapi import HTTPException, status

from app.access.base_access import access_model
from app.loaders.product import ProductLoader
from app.loaders.cart_product import CartProductLoader
from app.models import CartProduct

async def access_cart_product(**kwargs) -> Optional[CartProduct | HTTPException]:
    if kwargs['method'] == 'post':
        try:
            # TODO добавить получение цены товара
            product = await ProductLoader.get(kwargs['dto']['product_id'])
            if not product:
                return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product with such id not found")
            kwargs['dto']['price_at_time'] = product.price

            cart_product = await CartProductLoader.create(**kwargs['dto'])
            return await cart_product.to_dict()
        except Exception as e:
            return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    elif kwargs['method'] == 'patch':
        try:
            # TODO добавить получение цены товара
            product = await ProductLoader.get(kwargs['dto']['product_id'])
            if not product:
                return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product with such id not found")
            kwargs['dto']['price_at_time'] = product.price

            cart_product = await CartProductLoader.update(**kwargs['dto'])
            return await cart_product.to_dict()
        except Exception as e:
            return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    else:
        return await access_model(loader_class=CartProductLoader, **kwargs)