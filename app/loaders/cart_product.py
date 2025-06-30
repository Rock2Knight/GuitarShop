from typing import override

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import connection
from app.models import CartProduct
from app.loaders.model_loader import ModelLoader

class CartProductLoader(ModelLoader[CartProduct]):
    model: CartProduct = CartProduct

    @classmethod
    @override
    @connection
    async def create(cls, session: AsyncSession, **kwargs):
        cart_product = cls.model(**kwargs)
        session.add(cart_product)
        try:
            await session.commit()
            await session.refresh(cart_product)
        except Exception as e:
            await session.rollback()
            raise e

        return cart_product
    

    @classmethod
    @override
    @connection
    async def update(cls, session: AsyncSession, **kwargs):
        cart_product_id = kwargs.pop('item_id')

        query_select = select(cls.model).filter_by(id=cart_product_id)
        cart_product = await session.scalars(query_select)

        product_ids = {"guitar_id", "combo_id", "processor_id", "effect_id"}
        provided_ids = {k: v for k, v in kwargs.items() if k in product_ids and v is not None}

        if len(provided_ids) > 1:
            raise ValueError("Передано больше одного FK на товар")

        if provided_ids:
            for fk in product_ids:
                setattr(cart_product, fk, None)
            for fk, value in provided_ids.items():
                setattr(cart_product, fk, value)

        if "quantity" in kwargs.keys():
            cart_product.quantity = kwargs["quantity"]
        if "cart_id" in kwargs.keys():
            cart_product.cart_id = kwargs["cart_id"]

        try:
            await session.commit()
            await session.refresh(cart_product)
            return cart_product
        except Exception as e:
            await session.rollback()
            raise e