"""This module contains tests for guitar processors."""
import pytest
from sqlalchemy import select, delete

from models import Processor


@pytest.mark.asyncio(scope="session")
async def test_get_processor(client, async_session_maker, model_factory, test_data, removed_keys):
    """Testing get a processor by id."""
    test_json = test_data["FIRST_EXPECTED_PROCESSOR"]
    description = test_json.pop("description")

    async with async_session_maker() as async_session:
        query = delete(Processor)
        query = query.filter_by(name=test_json["name"])
        await async_session.execute(query)
        await async_session.commit()

    expected_processor = await model_factory.create(
        model_class=Processor,
        **test_json
    )

    response = await client.get(f"/processor/{expected_processor.id}")
    assert response.status_code in (200, 201)

    test_json["description"] = description
    response_body = response.json()
    response_body = {k: v for k, v in response_body.items() if k not in removed_keys}
    assert response_body == test_json
    
    async with async_session_maker() as async_session:
        await model_factory.delete(async_session, expected_processor)


@pytest.mark.asyncio(scope="session")
async def test_create_processor(client, async_session_maker, test_data):
    """Testing create a processor by POST-request."""
    test_json = test_data["TEST_BODY_FOR_PROCESSOR"]
    async with async_session_maker() as async_session:
        query = delete(Processor)
        query = query.filter_by(name=test_json["name"])
        await async_session.execute(query)
        await async_session.commit()

    response = await client.post("/processor/", json=test_json)
    response_body = response.json()

    assert response.status_code == 201

    created_processor = None

    async with async_session_maker() as async_session:
        name = response_body["name"]
        created_processor = await async_session.execute(
            select(Processor).where(Processor.name == name)
        )
        created_processor = created_processor.scalars().first()
        created_processor = await created_processor.to_dict()

    for key in (k for k in created_processor.keys() if k in test_json.keys()):
        assert created_processor.get(key) == test_json.get(key)


@pytest.mark.asyncio(scope="session")
async def test_update_processor(client, model_factory, async_session_maker, test_data):
    """Testing partial update of a processor by PATCH-request."""
    test_json_create = test_data["TEST_BODY_FOR_PROCESSOR"]
    test_json_update = test_data["TEST_UPDATED_DATA_FOR_PROCESSOR"]

    async with async_session_maker() as async_session:
        query = delete(Processor)
        query = query.filter_by(name=test_json_create["name"])
        await async_session.execute(query)
        await async_session.commit()

    created_processor = await model_factory.create(
        model_class=Processor,
        **test_json_create
    )
    processor_id = created_processor.id

    response = await client.patch(
        f"/processor/{processor_id}",
        json=test_json_update
    )
    assert response.status_code == 201
    
    # Проверяем обновленные данные в БД
    async with async_session_maker() as async_session:
        updated_processor = await async_session.execute(
            select(Processor).
            where(Processor.id == processor_id)
        )
        updated_processor = updated_processor.scalars().first()
        updated_processor = await updated_processor.to_dict()
        
        # Проверяем обновленные поля
        for key in (k for k in updated_processor.keys() if k in test_json_update.keys()):
            assert updated_processor[key] == test_json_update[key]
        
        # Проверяем, что другие поля не изменились
        non_updated_keys = set(test_json_create.keys()) - set(test_json_update.keys())
        for key in (k for k in updated_processor.keys() if k in non_updated_keys):
            assert updated_processor[key] == test_json_create[key]

    async with async_session_maker() as async_session:
        await model_factory.delete(async_session, created_processor)


@pytest.mark.asyncio(scope="session")
async def test_delete_processor(client, model_factory, async_session_maker, test_data):
    """Testing deletion of a processor by DELETE-request."""
    test_json = test_data["TEST_BODY_FOR_PROCESSOR"]

    async with async_session_maker() as async_session:
        query = delete(Processor)
        query = query.filter_by(name=test_json["name"])
        await async_session.execute(query)
        await async_session.commit()

    created_processor = await model_factory.create(
        model_class=Processor,
        **test_json
    )
    processor_id = created_processor.id

    response = await client.delete(f"/processor/{processor_id}")
    assert response.status_code == 200
    
    async with async_session_maker() as async_session:
        deleted_processor = await async_session.execute(
            select(Processor).
            where(Processor.id == processor_id)
        )
        assert deleted_processor.scalars().first() is None
