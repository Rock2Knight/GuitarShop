"""This module contains tests for guitar processors."""
import pytest
from sqlalchemy import select, delete
from logger import logger

from models import EffectPedal


@pytest.mark.asyncio(scope="session")
async def test_get_effect(client, async_session_maker, model_factory, test_data, removed_keys):
    """Testing get a effect pedal by id."""
    test_json = test_data["FIRST_EXPECTED_EFFECT"]
    description = test_json.pop("description")

    async with async_session_maker() as async_session:
        query = delete(EffectPedal)
        query = query.filter_by(name=test_json["name"])
        await async_session.execute(query)
        await async_session.commit()

    expected_effect = await model_factory.create(
        model_class=EffectPedal,
        **test_json
    )

    response = await client.get(f"/effect/{expected_effect.id}")
    response_body = response.json()
    logger.debug(f"Response: {response_body}")
    assert response.status_code in (200, 201)

    test_json["description"] = description
    response_body = response.json()
    response_body = {k: v for k, v in response_body.items() if k not in removed_keys}
    assert response_body == test_json
    
    async with async_session_maker() as async_session:
        await model_factory.delete(async_session, expected_effect)


@pytest.mark.asyncio(scope="session")
async def test_create_effect(client, async_session_maker, test_data):
    """Testing create a effect pedal by POST-request."""
    test_json = test_data["TEST_BODY_FOR_EFFECT"]
    async with async_session_maker() as async_session:
        query = delete(EffectPedal)
        query = query.filter_by(name=test_json["name"])
        await async_session.execute(query)
        await async_session.commit()

    response = await client.post("/effect/", json=test_json)
    response_body = response.json()

    assert response.status_code == 201

    created_effect = None

    async with async_session_maker() as async_session:
        name = response_body["name"]
        created_effect = await async_session.execute(
            select(EffectPedal).where(EffectPedal.name == name)
        )
        created_effect = created_effect.scalars().first()
        created_effect = await created_effect.to_dict()

    for key in (k for k in created_effect.keys() if k in test_json.keys()):
        assert created_effect.get(key) == test_json.get(key)


@pytest.mark.asyncio(scope="session")
async def test_update_effect(client, model_factory, async_session_maker, test_data):
    """Testing partial update of a effect pedal by PATCH-request."""
    test_json_create = test_data["TEST_BODY_FOR_EFFECT"]
    test_json_update = test_data["TEST_UPDATED_DATA_FOR_EFFECT"]

    async with async_session_maker() as async_session:
        query = delete(EffectPedal)
        query = query.filter_by(name=test_json_create["name"])
        await async_session.execute(query)
        await async_session.commit()

    created_effect = await model_factory.create(
        model_class=EffectPedal,
        **test_json_create
    )
    effect_id = created_effect.id

    response = await client.patch(
        f"/effect/{effect_id}",
        json=test_json_update
    )
    assert response.status_code == 201
    
    # Проверяем обновленные данные в БД
    async with async_session_maker() as async_session:
        updated_effect = await async_session.execute(
            select(EffectPedal).
            where(EffectPedal.id == effect_id)
        )
        updated_effect = updated_effect.scalars().first()
        updated_effect = await updated_effect.to_dict()
        
        # Проверяем обновленные поля
        for key in (k for k in updated_effect.keys() if k in test_json_update.keys()):
            assert updated_effect[key] == test_json_update[key]
        
        # Проверяем, что другие поля не изменились
        non_updated_keys = set(test_json_create.keys()) - set(test_json_update.keys())
        for key in (k for k in updated_effect.keys() if k in non_updated_keys):
            assert updated_effect[key] == test_json_create[key]

    async with async_session_maker() as async_session:
        await model_factory.delete(async_session, created_effect)


@pytest.mark.asyncio(scope="session")
async def test_delete_effect(client, model_factory, async_session_maker, test_data):
    """Testing deletion of a effect pedal by DELETE-request."""
    test_json = test_data["TEST_BODY_FOR_EFFECT"]

    async with async_session_maker() as async_session:
        query = delete(EffectPedal)
        query = query.filter_by(name=test_json["name"])
        await async_session.execute(query)
        await async_session.commit()

    created_effect = await model_factory.create(
        model_class=EffectPedal,
        **test_json
    )
    effect_id = created_effect.id

    response = await client.delete(f"/effect/{effect_id}")
    assert response.status_code == 200
    
    async with async_session_maker() as async_session:
        deleted_effect = await async_session.execute(
            select(EffectPedal).
            where(EffectPedal.id == effect_id)
        )
        assert deleted_effect.scalars().first() is None
