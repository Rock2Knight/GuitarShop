from sqlalchemy.ext.asyncio import AsyncSession

from database import connection

from models import Order, OrderProduct
from loaders.model_loader import ModelLoader

class OrderProductLoader(ModelLoader):
    model: OrderProduct = OrderProduct

    @classmethod
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