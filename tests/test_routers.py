import asyncio
import ctypes
import threading
from datetime import datetime

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Integer, func, select
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column, class_mapper
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from logger import logger

from config import settings
from main import app
from models import *

DATABASE_URL = settings.get_db_url()

FIRST_EXPECTED_GUITAR = {
    "guitar_type": "Electric",
    "shape": "Stratocaster",
    "fret_count": 25,
    "recorder_config": "s-s-h",
    "fingerboard_material": "afdsfasdfs",
    "body_material": "тополь",
    "product_type": "Guitar",
    "name": "ROCKDALE Stars Black Limited Edition HSS BK",
    "description": "afadsfdas",
    "quantity": 30,
    "price": 12000,
    "id": 1,
    "created_at": "2025-06-23T16:16:12.419956",
    "updated_at": "2025-06-24T10:45:29.256923"
}


TEST_BODY_FOR_CREATED_GUITAR = {
    "product_type": "Guitar",
    "name": "ROCKDALE Stars TE HH Black",
    "quantity": 22,
    "price": 11100,
    "guitar_type": "Electric",
    "shape": "Telecaster",
    "fret_count": 22,
    "recorder_config": "h-h",
    "fingerboard_material": "клен",
    "body_material": "тополь"
}


@pytest.mark.asyncio(scope="session")
async def test_get_guitar():
    address = id(asyncio.get_running_loop())
    logger.debug(f"Loop of function test_get_guitar: {threading.current_thread().name}: {id(address)}")

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/guitar/1")
    assert response.status_code in (200, 201)
    assert response.json() == FIRST_EXPECTED_GUITAR


@pytest.mark.asyncio(scope="session")
async def test_create_guitar(client, async_session_maker):
    address = id(asyncio.get_running_loop())
    logger.debug(f"Loop of function test_create_guitar: {threading.current_thread().name}: {id(address)}")

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("/guitar/", json=TEST_BODY_FOR_CREATED_GUITAR)
    #response = await client.post("/guitar/", json=TEST_BODY_FOR_CREATED_GUITAR)
    assert response.status_code == 201

    response_body = response.json()
    created_guitar = None

    async with async_session_maker() as async_session:
        date_str = response_body["created_at"]
        time_from_response = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
        created_guitar = await async_session.execute(select(Guitar).where(Guitar.created_at == time_from_response))
        created_guitar = created_guitar.scalars().first()
        created_guitar = await created_guitar.to_dict()

    # TODO: compare created_guitar with TEST_BODY_FOR_CREATED_GUITAR
    for key in (k for k in created_guitar.keys() if k in TEST_BODY_FOR_CREATED_GUITAR.keys()):
        assert created_guitar.get(key) == TEST_BODY_FOR_CREATED_GUITAR.get(key)