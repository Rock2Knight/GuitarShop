"""This module contains tests for combo amplifiers."""
import pytest
from sqlalchemy import select, delete

from models import ComboAmplifier


@pytest.mark.asyncio(scope="session")
async def test_get_combo_ampf(client, async_session_maker, model_factory, test_data, removed_keys):
    """Testing get a combo amplifier by id."""
    test_json = test_data["FIRST_EXPECTED_COMBO_AMPLIFIER"]
    description = test_json.pop("description")

    async with async_session_maker() as async_session:
        query = delete(ComboAmplifier)
        query = query.filter_by(name=test_json["name"])
        await async_session.execute(query)
        await async_session.commit()

    expected_combo_ampf = await model_factory.create(
        model_class=ComboAmplifier,
        **test_json
    )

    response = await client.get(f"/combo_ampf/{expected_combo_ampf.id}")
    assert response.status_code in (200, 201)

    test_json["description"] = description
    response_body = response.json()
    response_body = {k: v for k, v in response_body.items() if k not in removed_keys}
    assert response_body == test_json
    
    async with async_session_maker() as async_session:
        await model_factory.delete(async_session, expected_combo_ampf)


@pytest.mark.asyncio(scope="session")
async def test_create_combo_ampf(client, async_session_maker, test_data):
    """Testing create a combo amplifier by POST-request."""
    test_json = test_data["TEST_BODY_FOR_COMBO_AMPLIFIER"]
    async with async_session_maker() as async_session:
        query = delete(ComboAmplifier)
        query = query.filter_by(name=test_json["name"])
        await async_session.execute(query)
        await async_session.commit()

    response = await client.post("/combo_ampf/", json=test_json)
    response_body = response.json()

    assert response.status_code == 201

    created_combo_ampf = None

    async with async_session_maker() as async_session:
        name = response_body["name"]
        created_combo_ampf = await async_session.execute(
            select(ComboAmplifier).where(ComboAmplifier.name == name)
        )
        created_combo_ampf = created_combo_ampf.scalars().first()
        created_combo_ampf = await created_combo_ampf.to_dict()

    for key in (k for k in created_combo_ampf.keys() if k in test_json.keys()):
        assert created_combo_ampf.get(key) == test_json.get(key)


@pytest.mark.asyncio(scope="session")
async def test_update_combo_ampf(client, model_factory, async_session_maker, test_data):
    """Testing partial update of a combo amplifier by PATCH-request."""
    test_json_create = test_data["TEST_BODY_FOR_COMBO_AMPLIFIER"]
    test_json_update = test_data["TEST_UPDATED_DATA_FOR_COMBO_AMPLIFIER"]

    async with async_session_maker() as async_session:
        query = delete(ComboAmplifier)
        query = query.filter_by(name=test_json_create["name"])
        await async_session.execute(query)
        await async_session.commit()

    created_combo_ampf = await model_factory.create(
        model_class=ComboAmplifier,
        **test_json_create
    )
    combo_ampf_id = created_combo_ampf.id

    response = await client.patch(
        f"/combo_ampf/{combo_ampf_id}",
        json=test_json_update
    )
    assert response.status_code == 201
    
    # Проверяем обновленные данные в БД
    async with async_session_maker() as async_session:
        updated_combo_ampf = await async_session.execute(
            select(ComboAmplifier).
            where(ComboAmplifier.id == combo_ampf_id)
        )
        updated_combo_ampf = updated_combo_ampf.scalars().first()
        updated_combo_ampf = await updated_combo_ampf.to_dict()
        
        # Проверяем обновленные поля
        for key in (k for k in updated_combo_ampf.keys() if k in test_json_update.keys()):
            assert updated_combo_ampf[key] == test_json_update[key]
        
        # Проверяем, что другие поля не изменились
        non_updated_keys = set(test_json_create.keys()) - set(test_json_update.keys())
        for key in (k for k in updated_combo_ampf.keys() if k in non_updated_keys):
            assert updated_combo_ampf[key] == test_json_create[key]

    async with async_session_maker() as async_session:
        await model_factory.delete(async_session, created_combo_ampf)


@pytest.mark.asyncio(scope="session")
async def test_delete_combo_ampf(client, model_factory, async_session_maker, test_data):
    """Testing deletion of a combo amplifier by DELETE-request."""
    test_json = test_data["TEST_BODY_FOR_COMBO_AMPLIFIER"]

    async with async_session_maker() as async_session:
        query = delete(ComboAmplifier)
        query = query.filter_by(name=test_json["name"])
        await async_session.execute(query)
        await async_session.commit()

    created_combo_ampf = await model_factory.create(
        model_class=ComboAmplifier,
        **test_json
    )
    combo_ampf_id = created_combo_ampf.id

    response = await client.delete(f"/combo_ampf/{combo_ampf_id}")
    assert response.status_code == 200
    
    async with async_session_maker() as async_session:
        deleted_combo_ampf = await async_session.execute(
            select(ComboAmplifier).
            where(ComboAmplifier.id == combo_ampf_id)
        )
        assert deleted_combo_ampf.scalars().first() is None
