from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import connection
from app.models import Cart
from app.loaders.model_loader import ModelLoader

class CartLoader(ModelLoader[Cart]):
    model: Cart = Cart

    @classmethod
    @connection
    async def get_by_user_id(cls, session: AsyncSession, user_id: int) -> Cart:
        query_select = select(cls.model).filter_by(user_id=user_id)
        cart = await session.scalars(query_select)
        return cart.first()
    