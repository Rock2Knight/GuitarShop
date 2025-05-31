from typing import Type, TypeVar, Any

from loguru import logger
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database import connection

T = TypeVar('T')  # Generic тип для модели

class ModelLoader:
    model: Type[T]  # Должен быть переопределен в дочерних классах

    @classmethod
    @connection
    async def get(cls, session: AsyncSession, item_id: int) -> T | None:
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
    async def create(cls, session: AsyncSession, **kwargs) -> T:
        """
        Создает новый объект
        """
        item = cls.model(**kwargs)
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return item


    @classmethod
    @connection
    async def update(cls, session: AsyncSession, item_id: int, **kwargs) -> T | None:
        """
        Обновляет объект
        """
        query_select = select(cls.model).filter_by(id=item_id)
        item = await session.scalars(query_select)

        if not item:
            return None
        
        item = item.first()
        if not item:
            return None
            
        for key, value in kwargs.items():
            setattr(item, key, value)
            
        await session.commit()
        await session.refresh(item)
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