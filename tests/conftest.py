""" This module prepares test data """
import json
from typing import Type, TypeVar, Any, AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.config import settings
from app.database import Base
from app.main import app

Model = TypeVar("Model", bound=Base)

@pytest.fixture
def removed_keys():
    return {"created_at", "updated_at", "id"}


@pytest_asyncio.fixture(scope="session")
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture(scope="session")
async def async_session_maker():
    """Genrate an async session creating requests to database for testing."""
    engine = create_async_engine(settings.get_db_url())
    yield async_sessionmaker(engine, expire_on_commit=False)
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def test_data():
    """Take test data from json file."""
    with open("tests/testdata.json", "r") as json_test_data:
        test_data = json.load(json_test_data)
        yield test_data


class ModelFactory:
    """Абстрактная фабрика для создания тестовых моделей."""
    
    @classmethod
    async def create(
        cls, 
        async_session: AsyncSession,
        model_class: Type[Model],
        **kwargs: Any
    ) -> Model:
        """Создает и возвращает экземпляр модели с переданными атрибутами."""
        instance = model_class(**kwargs)
        async_session.add(instance)
        await async_session.commit()
        await async_session.refresh(instance)
        return instance


    @classmethod
    async def delete(
        cls,
        async_session: AsyncSession,
        instance: Model
    ) -> None:
        """Удаляет созданный экземпляр."""
        await async_session.delete(instance)
        await async_session.commit()


@pytest_asyncio.fixture(scope="session")
async def model_factory(async_session_maker) -> AsyncGenerator:
    """Возвращает экземпляр фабрики с привязанной сессией БД."""
    
    class Factory(ModelFactory):

        @classmethod
        async def create(
            cls, 
            model_class: Type[Model],
            **kwargs
        ) -> Model:
            async with async_session_maker() as async_session:
                return await super().create(async_session, model_class, **kwargs)
            
    yield Factory
