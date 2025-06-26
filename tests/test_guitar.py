"""This module contains tests for guitars."""
from datetime import datetime
import asyncio

import pytest
from sqlalchemy import select, delete

from models import Guitar
from logger import logger


@pytest.mark.asyncio(scope="session")
async def test_get_guitar(client, test_data):
    """Testing get a guitar by id."""
    response = await client.get("/guitar/1")
    assert response.status_code in (200, 201)
    assert response.json() == test_data["FIRST_EXPECTED_GUITAR"]


@pytest.mark.asyncio(scope="session")
async def test_create_guitar(client, async_session_maker, test_data):
    """Testing create a guitar by POST-request."""
    TEST_BODY_FOR_CREATED_GUITAR = test_data["TEST_BODY_FOR_CREATED_GUITAR"]
    async with async_session_maker() as async_session:
        query_delete = delete(Guitar).filter_by(name=TEST_BODY_FOR_CREATED_GUITAR["name"])
        await async_session.execute(query_delete)
        await async_session.commit()

    response = await client.post("/guitar/", json=TEST_BODY_FOR_CREATED_GUITAR)
    assert response.status_code == 201

    response_body = response.json()
    print(f"Response body {response_body}")
    created_guitar = None

    async with async_session_maker() as async_session:
        name = response_body["name"]
        created_guitar = await async_session.execute(select(Guitar).where(Guitar.name == name))
        created_guitar = created_guitar.scalars().first()
        created_guitar = await created_guitar.to_dict()

    for key in (k for k in created_guitar.keys() if k in TEST_BODY_FOR_CREATED_GUITAR.keys()):
        assert created_guitar.get(key) == TEST_BODY_FOR_CREATED_GUITAR.get(key)
