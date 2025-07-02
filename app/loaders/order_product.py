from typing import override

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