"""This module contains tests for guitars."""
import pytest
from sqlalchemy import select, delete

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
        created_guitar = await async_session.execute(
            select(Guitar).where(Guitar.name == name)
        )
        created_guitar = created_guitar.scalars().first()
        created_guitar = await created_guitar.to_dict()

    for key in (k for k in created_guitar.keys() if k in TEST_BODY_FOR_CREATED_GUITAR.keys()):
        assert created_guitar.get(key) == TEST_BODY_FOR_CREATED_GUITAR.get(key)


@pytest.mark.asyncio(scope="session")
async def test_update_guitar(client, async_session_maker, test_data):
    """Testing partial update of a guitar by PATCH-request."""
    TEST_BODY_FOR_CREATED_GUITAR = test_data["TEST_BODY_FOR_CREATED_GUITAR"]
    TEST_UPDATED_DATA_FOR_GUITAR = test_data["TEST_UPDATED_DATA_FOR_GUITAR"]

    async with async_session_maker() as async_session:
        query_delete = delete(Guitar).filter_by(
            name=TEST_BODY_FOR_CREATED_GUITAR["name"])
        await async_session.execute(query_delete)
        await async_session.commit()

    response = await client.post(
        "/guitar/",
        json=test_data["TEST_BODY_FOR_CREATED_GUITAR"]
    )
    created_guitar = None

    async with async_session_maker() as async_session:
        name = response.json()["name"]
        created_guitar = await async_session.execute(
            select(Guitar).
            where(Guitar.name == name)
        )
        created_guitar = created_guitar.scalars().first()
        created_guitar = await created_guitar.to_dict()
    
    guitar_id = created_guitar["id"]
    response = await client.patch(
        f"/guitar/{guitar_id}",
        json=TEST_UPDATED_DATA_FOR_GUITAR
    )
    assert response.status_code == 201
    
    # Проверяем обновленные данные в БД
    async with async_session_maker() as async_session:
        updated_guitar = await async_session.execute(
            select(Guitar).
            where(Guitar.id == guitar_id)
        )
        updated_guitar = updated_guitar.scalars().first()
        updated_guitar = await updated_guitar.to_dict()
        
        # Проверяем обновленные поля
        for key in (k for k in updated_guitar.keys() if k in TEST_UPDATED_DATA_FOR_GUITAR.keys()):
            assert updated_guitar[key] == TEST_UPDATED_DATA_FOR_GUITAR[key]
        
        # Проверяем, что другие поля не изменились
        not_updated_keys = set(TEST_BODY_FOR_CREATED_GUITAR.keys()) - set(TEST_UPDATED_DATA_FOR_GUITAR.keys())
        for key in (k for k in updated_guitar.keys() if k in not_updated_keys):
            assert updated_guitar[key] == TEST_BODY_FOR_CREATED_GUITAR[key]


@pytest.mark.asyncio(scope="session")
async def test_delete_guitar(client, async_session_maker, test_data):
    """Testing deletion of a guitar by DELETE-request."""
    TEST_BODY_FOR_CREATED_GUITAR = test_data["TEST_BODY_FOR_CREATED_GUITAR"]

    async with async_session_maker() as async_session:
        query_delete = delete(Guitar).filter_by(name=TEST_BODY_FOR_CREATED_GUITAR["name"])
        await async_session.execute(query_delete)
        await async_session.commit()

    post_response = await client.post(
        "/guitar/",
        json=test_data["TEST_BODY_FOR_CREATED_GUITAR"]
    )
    created_guitar = None
    
    async with async_session_maker() as async_session:
        name = post_response.json()["name"]
        created_guitar = await async_session.execute(
            select(Guitar).
            where(Guitar.name == name)
        )
        created_guitar = created_guitar.scalars().first()
        created_guitar = await created_guitar.to_dict()

    guitar_id = created_guitar["id"]
    delete_response = await client.delete(f"/guitar/{guitar_id}")
    assert delete_response.status_code == 200
    
    async with async_session_maker() as async_session:
        deleted_guitar = await async_session.execute(
            select(Guitar).
            where(Guitar.id == guitar_id)
        )
        assert deleted_guitar.scalars().first() is None
