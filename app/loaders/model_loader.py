from abc import ABC
from typing import Type, Any, ClassVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.logger import logger
from app.database import connection


class ModelLoader[ModelClass](ABC):
    model: ClassVar[type[ModelClass]]

    @classmethod
    @connection
    async def get(cls, session: AsyncSession, item_id: int) -> ModelClass | None:
        """
        Получает объект по ID
        """
        logger.info(f"Get-request is handled in ModelLoader.get()")
        logger.info(f"Model type = {cls.model}")

        query = select(cls.model).filter_by(id=item_id)
        result = await session.scalars(query)
        return result.first()


    @classmethod
    @connection
    async def create(cls, session: AsyncSession, **kwargs) -> ModelClass:
        """
        Создает новый объект
        """
        item = cls.model(**kwargs)
        session.add(item)
        try:
            await session.commit()
            await session.refresh(item)
        except Exception as e:
            await session.rollback()
            raise e
        return item


    @classmethod
    @connection
    async def update(cls, session: AsyncSession, **kwargs) -> ModelClass | None:
        """
        Обновляет объект
        """
        item_id = kwargs.pop('item_id')

        query_select = select(cls.model).filter_by(id=item_id)
        item = await session.scalars(query_select)

        if not item:
            return None
        
        item = item.first()
        if not item:
            return None
            
        for key, value in kwargs.items():
            setattr(item, key, value)

        try:    
            await session.commit()
            await session.refresh(item)
        except Exception as e:
            await session.rollback()
            raise e
        return item


    @classmethod
    @connection
    async def delete(cls, session: AsyncSession, item_id: int) -> dict[str, Any]:
        """
        Удаляет объект и возвращает его данные в виде словаря
        """
        query_select = select(cls.model).filter_by(id=item_id)
        item = await session.scalars(query_select)

        if item is None:
            raise ValueError(f'{cls.model.__name__} {item_id} not found')
        item = item.first()
        if item is None:
            raise ValueError(f'{cls.model.__name__} {item_id} not found')
            
        item_dict = await item.to_dict()
        await session.delete(item)
        await session.commit()
        return item_dict