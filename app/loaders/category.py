from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import connection
from app.models import Category
from app.loaders.model_loader import ModelLoader

class CategoryLoader(ModelLoader[Category]):
    model: Category = Category

    @classmethod
    @connection
    async def get_category_by_name(cls, session: AsyncSession, category_name: str) -> Category | None:
        """
        Получает категорию по имени
        """
        query = select(cls.model).filter_by(name=category_name)
        result = await session.scalars(query)
        res = result.one_or_none()
        return res