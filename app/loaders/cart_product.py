from typing import override

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import connection
from app.models import CartProduct
from app.loaders.model_loader import ModelLoader

class CartProductLoader(ModelLoader[CartProduct]):
    model: CartProduct = CartProduct

    @classmethod
    @connection
    async def get_by_cart_id(cls, session: AsyncSession, cart_id: int) -> list[CartProduct]:
        query = select(cls.model).where(cls.model.cart_id == cart_id).order_by(cls.model.id)
        result = await session.scalars(query)
        return result.all()