from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import connection
from app.models import Attributes
from app.loaders.model_loader import ModelLoader

class AttributesLoader(ModelLoader[Attributes]):
    model: Attributes = Attributes

    @classmethod
    @connection
    async def get_attribute_by_name(cls, session: AsyncSession, name: str) -> Attributes:
        """
        Получает атрибут по имени и категории
        """
        query = select(cls.model).filter_by(name=name)
        result = await session.scalars(query)
        return result.one_or_none()
