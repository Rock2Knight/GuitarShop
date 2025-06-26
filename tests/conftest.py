import json

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import settings
from main import app


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
