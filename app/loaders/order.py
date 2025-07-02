from random import randint
from typing import override
from datetime import datetime, timedelta, date

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import connection
from app.models import Order, OrderStatus
from app.loaders.model_loader import ModelLoader

class OrderLoader(ModelLoader[Order]):
    model: Order = Order

    @classmethod
    @override
    @connection
    async def create(cls, session: AsyncSession, user_id: int) -> Order:
        time_offset = randint(7, 30)
        order_datetime = datetime.now().astimezone() + timedelta(days=time_offset)
        order_date = date(order_datetime.year, order_datetime.month, order_datetime.day)

        order = Order(
            user_id=user_id,
            order_date=order_date,
            status=OrderStatus.NEW
        )

        session.add(order)
        await session.commit()
        await session.refresh(order)
        return order


    @classmethod
    @override
    @connection
    async def delete(cls, session: AsyncSession, order_id: int) -> dict:
        query_order = select(Order).filter_by(id=order_id)
        order = await session.get(Order, order_id)
        
        if not order:
            raise Exception("Order does not exist")
        
        order_dict = await order.to_dict()
        await session.delete(order)
        await session.commit()

        return order_dict