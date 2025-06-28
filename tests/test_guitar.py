"""This module contains tests for guitars."""
import pytest
from sqlalchemy import select, delete

from models import Guitar


@pytest.mark.asyncio(scope="session")
async def test_get_guitar(client, async_session_maker, model_factory, test_data, removed_keys):
    """Testing get a guitar by id."""
    test_json = test_data["FIRST_EXPECTED_GUITAR"]
    description = test_json.pop("description")

    async with async_session_maker() as async_session:
        query = delete(Guitar).filter_by(name=test_json["name"])
        await async_session.execute(query)
        await async_session.commit()

    expected_guitar = await model_factory.create(
        model_class=Guitar, 
        **test_json
    )

    response = await client.get(f"/guitar/{expected_guitar.id}")
    assert response.status_code in (200, 201)

    test_json["description"] = description
    response_body = response.json()
    response_body = {k: v for k, v in response_body.items() if k not in removed_keys}
    assert response_body == test_json
    
    async with async_session_maker() as async_session:
        await model_factory.delete(async_session, expected_guitar)


@pytest.mark.asyncio(scope="session")
async def test_create_guitar(client, async_session_maker, test_data):
    """Testing create a guitar by POST-request."""
    test_json = test_data["TEST_BODY_FOR_CREATED_GUITAR"]
    async with async_session_maker() as async_session:
        query = delete(Guitar).filter_by(name=test_json["name"])
        await async_session.execute(query)
        await async_session.commit()

    response = await client.post("/guitar/", json=test_json)
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

    for key in (k for k in created_guitar.keys() if k in test_json.keys()):
        assert created_guitar.get(key) == test_json.get(key)


@pytest.mark.asyncio(scope="session")
async def test_update_guitar(client, async_session_maker, test_data):
    """Testing partial update of a guitar by PATCH-request."""
    test_json_create = test_data["TEST_BODY_FOR_CREATED_GUITAR"]
    test_json_update = test_data["TEST_UPDATED_DATA_FOR_GUITAR"]

    async with async_session_maker() as async_session:
        query = delete(Guitar)
        query = query.filter_by(name=test_json_create["name"])
        await async_session.execute(query)
        await async_session.commit()

    response = await client.post(
        "/guitar/",
        json=test_json_create
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
        json=test_json_update
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
        for key in (k for k in updated_guitar.keys() if k in test_json_update.keys()):
            assert updated_guitar[key] == test_json_update[key]
        
        # Проверяем, что другие поля не изменились
        non_updated_keys = set(test_json_create.keys()) - set(test_json_update.keys())
        for key in (k for k in updated_guitar.keys() if k in non_updated_keys):
            assert updated_guitar[key] == test_json_create[key]


@pytest.mark.asyncio(scope="session")
async def test_delete_guitar(client, model_factory, async_session_maker, test_data):
    """Testing deletion of a guitar by DELETE-request."""
    test_json = test_data["TEST_BODY_FOR_CREATED_GUITAR"]

    async with async_session_maker() as async_session:
        query = delete(Guitar).filter_by(name=test_json["name"])
        await async_session.execute(query)
        await async_session.commit()

    created_guitar = await model_factory.create(
        model_class=Guitar,
        **test_json
    )

    guitar_id = created_guitar.id
    response = await client.delete(f"/guitar/{guitar_id}")
    assert response.status_code == 200

    async with async_session_maker() as async_session:
        deleted_guitar = await async_session.execute(
            select(Guitar)
            .where(Guitar.id == guitar_id)
        )
        assert deleted_guitar.scalars().first() is None
