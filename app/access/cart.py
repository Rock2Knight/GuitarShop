from typing import Optional

from fastapi import HTTPException, status

from app.access.base_access import access_model
from app.loaders.product import ProductLoader
from app.loaders.cart import CartLoader
from app.loaders.cart_product import CartProductLoader
from app.models import CartProduct, Cart

async def access_cart(**kwargs) -> Optional[CartProduct | HTTPException]:
    if kwargs['method'] == 'get':
        try:
            cart_products_list = []
            total_price = 0

            cart = await CartLoader.get_by_user_id(user_id=kwargs['id'])
            if not cart:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with id={kwargs.get("id")} doesn't exist"
                )

            cart_products = await CartProductLoader.get_by_cart_id(cart_id=cart.id)
            for cart_product in cart_products:
                product = await ProductLoader.get(item_id=cart_product.product_id)
                cart_product_info = await cart_product.to_dict()
                cart_product_info["product_name"] = product.name
                cart_products_list.append(cart_product_info)
                total_price += cart_product_info["price_at_time"] * cart_product_info["quantity"]

            cart_info = await cart.to_dict()
            cart_info["total_price"] = total_price
            cart_info["products"] = cart_products_list
            
            return {"cart_products": cart_products_list, "total_price": total_price}
        except Exception as e:
            return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    else:
        method = kwargs.pop("method")
        return await access_model(loader_class=Cart, method=method, **kwargs)