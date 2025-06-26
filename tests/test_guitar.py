"""This module contains tests for guitars."""
from datetime import datetime

import pytest
from sqlalchemy import select

from models import Guitar


@pytest.mark.asyncio(scope="session")
async def test_get_guitar(client, test_data):
    """Testing get a guitar by id."""
    response = await client.get("/guitar/1")
    assert response.status_code in (200, 201)
    assert response.json() == test_data["FIRST_EXPECTED_GUITAR"]


@pytest.mark.asyncio(scope="session")
async def test_create_guitar(client, async_session_maker, test_data):
    """Testing create a guitar by POST-request."""
    response = await client.post("/guitar/", json=test_data["TEST_BODY_FOR_CREATED_GUITAR"])
    assert response.status_code == 201

    response_body = response.json()
    created_guitar = None

    async with async_session_maker() as async_session:
        date_str = response_body["created_at"]
        time_from_response = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
        created_guitar = await async_session.execute(select(Guitar).where(Guitar.created_at == time_from_response))
        created_guitar = created_guitar.scalars().first()
        created_guitar = await created_guitar.to_dict()

    for key in (k for k in created_guitar.keys() if k in test_data["TEST_BODY_FOR_CREATED_GUITAR"].keys()):
        assert created_guitar.get(key) == test_data["TEST_BODY_FOR_CREATED_GUITAR"].get(key)
