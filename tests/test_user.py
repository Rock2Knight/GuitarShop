"""Base module for testing http-methods of users"""
from typing import Type, TypeVar, Any

import pytest
from sqlalchemy import select, delete

from app.models import User, Cart, ModelClass
from app.logger import logger

@pytest.mark.asyncio(scope="session")
async def test_get_user(client, async_session_maker, model_factory, removed_keys, test_data):
    """Testing get an user by id."""
    test_json = test_data["FIRST_EXPECTED_USER"]

    async with async_session_maker() as async_session:
        query = delete(User)
        query = query.filter_by(email=test_json["email"])
        await async_session.execute(query)
        await async_session.commit()

    test_json["passhash"] = hash(test_json.pop("password"))  # Находим хэш для пароля
    expected_user = await model_factory.create(
        model_class=User,
        **test_json
    )

    response = await client.get(f"/user/{expected_user.id}")
    response_body = response.json()
    #logger.debug(f"Response body::{cls.product}: {response_body}")
    assert response.status_code in (200, 201)

    test_json.pop("passhash")
    response_body = response.json()
    response_body = {k: v for k, v in response_body.items() if k not in removed_keys}
    assert response_body == test_json
    
    async with async_session_maker() as async_session:
        await model_factory.delete(async_session, expected_user)


@pytest.mark.asyncio(scope="session")
async def test_create_user(client, async_session_maker, test_data):
    """Testing create an user by POST-request."""
    test_json = test_data["TEST_BODY_FOR_USER"]
    async with async_session_maker() as async_session:
        query = delete(User)
        query = query.filter_by(email=test_json["email"])
        await async_session.execute(query)
        await async_session.commit()

    response = await client.post(f"/user/", json=test_json)
    response_body = response.json()

    assert response.status_code == 201

    created_user = None

    async with async_session_maker() as async_session:
        email = response_body["email"]
        created_user = await async_session.execute(
            select(User).where(User.email == email)
        )
        created_user = created_user.scalars().first()
        created_user = await created_user.to_dict()

    for key in (k for k in created_user.keys() if k in test_json.keys()):
        assert created_user.get(key) == test_json.get(key)


@pytest.mark.asyncio(scope="session")
async def test_update_user(client, model_factory, async_session_maker, test_data):
    """Testing partial update of an user by PATCH-request."""
    test_json_create = test_data["TEST_BODY_FOR_USER"]
    test_json_update = test_data["TEST_UPDATED_DATA_FOR_USER"]

    async with async_session_maker() as async_session:
        query = delete(User)
        query = query.filter_by(email=test_json_create["email"])
        await async_session.execute(query)
        await async_session.commit()

    test_json_create["passhash"] = hash(test_json_create.pop("password"))
    created_user = await model_factory.create(
        model_class=User,
        **test_json_create
    )
    user_id = created_user.id

    response = await client.patch(
        f"/user/{user_id}",
        json=test_json_update
    )
    response_body = response.json()
    logger.debug(f"Response: {response_body}")
    assert response.status_code == 201
    
    # Проверяем обновленные данные в БД
    async with async_session_maker() as async_session:
        updated_user = await async_session.execute(
            select(User).
            where(User.id == user_id)
        )
        updated_user = updated_user.scalars().first()
        updated_user = await updated_user.to_dict()
        
        # Проверяем обновленные поля
        for key in (k for k in updated_user.keys() if k in test_json_update.keys()):
            assert updated_user[key] == test_json_update[key]
        
        # Проверяем, что другие поля не изменились
        non_updated_keys = set(test_json_create.keys()) - set(test_json_update.keys())
        for key in (k for k in updated_user.keys() if k in non_updated_keys):
            assert updated_user[key] == test_json_create[key]

    async with async_session_maker() as async_session:
        await model_factory.delete(async_session, created_user)



@pytest.mark.asyncio(scope="session")
async def test_delete_product(client, model_factory, async_session_maker, test_data):
    """Testing deletion of a user by DELETE-request."""
    test_json = test_data["TEST_BODY_FOR_USER"]

    async with async_session_maker() as async_session:
        query = delete(User)
        query = query.filter_by(email=test_json["email"])
        await async_session.execute(query)
        await async_session.commit()

    if password := test_json.pop("password", None):
        test_json["passhash"] = hash(password)
    else:
        test_json["passhash"] = hash("fasdofkn3rjj3k3j2k")

    created_user = await model_factory.create(
        model_class=User,
        **test_json
    )
    user_id = created_user.id
    
    test_data_for_cart = {"user_id": user_id}
    created_user.cart = await model_factory.create(
        model_class=Cart,
        **test_data_for_cart
    )
    bound_cart_id = created_user.cart.id

    response = await client.delete(f"/user/{user_id}")
    assert response.status_code == 200
    
    async with async_session_maker() as async_session:
        deleted_user = await async_session.execute(
            select(User).
            where(User.id == user_id)
        )
        assert deleted_user.scalars().first() is None

        deleted_cart = await async_session.execute(
            select(Cart).
            where(Cart.id == bound_cart_id)
        )
        assert deleted_cart.scalars().first() is None