import asyncio
import ctypes
import threading

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import settings
from main import app
from loguru import logger


#pytestmark = pytest.mark.asyncio

'''
@pytest.fixture()
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()
'''


@pytest_asyncio.fixture(scope="session")
async def client():
    address = id(asyncio.get_running_loop())
    logger.debug(f"Loop of fixture \"client\": {threading.current_thread().name}: {id(address)}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture(scope="session")
async def async_session_maker():
    address = id(asyncio.get_running_loop())
    logger.debug(f"Loop of function \"session\": {threading.current_thread().name}: {id(address)}")
    engine = create_async_engine(settings.get_db_url())
    yield async_sessionmaker(engine, expire_on_commit=False)
    await engine.dispose()