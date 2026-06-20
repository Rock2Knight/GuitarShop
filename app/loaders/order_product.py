from typing import override

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import connection
from app.models import Order, OrderProduct
from app.loaders.model_loader import ModelLoader

class OrderProductLoader(ModelLoader[OrderProduct]):
    model: OrderProduct = OrderProduct

    @classmethod
    @override
    @connection
    async def create(cls, session: AsyncSession, **kwargs) -> OrderProduct:
        order_id = kwargs.get("order_id")
        order = await session.get(Order, order_id)
        if order is None:
            raise ValueError("Order not found")
        
        order_product = cls.model(**kwargs)
        session.add(order_product)
        order.order_products.append(order_product)  # Устанавливает связь
        
        await session.commit()
        await session.refresh(order_product)  # Обновляем атрибуты
        
        return order_product


    @classmethod
    @connection
    async def get_all_products_of_order(cls, session: AsyncSession, order_id: int) -> list[OrderProduct]:
        query = select(cls.model).where(cls.model.order_id == order_id).order_by(cls.model.id)
        order_products = await session.scalars(query)
        return order_products.all()