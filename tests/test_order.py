"""Base module for testing http-methods of orders"""
from random import randint
from datetime import date, datetime, timedelta

import pytest
from sqlalchemy import select, delete
from loguru import logger

from app.models import User, Order
from app.cache.redis import cache


@pytest.mark.order
@pytest.mark.asyncio(scope="session")
async def test_get_order(client, async_session_maker, model_factory, removed_keys, test_data):
    """Testing get an order by GET-request."""
    test_user = test_data["TEST_BODY_FOR_USER1"].copy()
    
    async with async_session_maker() as async_session:
        query = delete(User)
        query = query.filter_by(email=test_user["email"])
        await async_session.execute(query)
        await async_session.commit()

    if "passhash" not in test_user.keys():
        if "password" in test_user.keys():
            test_user["passhash"] = hash(test_user.pop("password"))
        else:
            test_user["passhash"] = hash("sdfwegewbegrefr")

    user = await model_factory.create(model_class=User, **test_user)
    
    time_offset = randint(7, 30)
    order_datetime = datetime.now().astimezone() + timedelta(days=time_offset)
    order_date = date(
        order_datetime.year, 
        order_datetime.month, 
        order_datetime.day
    )


    order_data = {"user_id": user.id, "order_date": order_date, "status": "New"}
    order = await model_factory.create(model_class=Order, **order_data)
    order_data["order_date"] = order_data["order_date"].strftime("%Y-%m-%d")

    response = await client.get(f"/order/{order.id}")
    response_body = response.json()
    assert response.status_code in (200, 201)

    response_body = {k: v for k, v in response_body.items() if k not in removed_keys}
    assert response_body == order_data
    
    async with async_session_maker() as async_session:
        await model_factory.delete(async_session, user)


@pytest.mark.order
@pytest.mark.asyncio(scope="session")
async def test_create_order(client, async_session_maker, model_factory, test_data):
    """Testing create an order by POST-request."""
    test_user = test_data["TEST_BODY_FOR_USER1"].copy()
    async with async_session_maker() as async_session:
        query = delete(User)
        query = query.filter_by(email=test_user["email"])
        await async_session.execute(query)
        await async_session.commit()

    if "passhash" not in test_user.keys():
        if "password" in test_user.keys():
            test_user["passhash"] = hash(test_user.pop("password"))
        else:
            test_user["passhash"] = hash("sdfwegewbegrefr")

    user = await model_factory.create(model_class=User, **test_user)
    response = await client.post(f"/order/{user.id}")
    response_body = response.json()
    assert response.status_code == 201
    assert response_body["status"].lower() == "new"

    async with async_session_maker() as async_session:
        await model_factory.delete(async_session, user)


@pytest.mark.order
@pytest.mark.asyncio(scope="session")
async def test_get_from_cache_order(client, model_factory, async_session_maker, test_data):
    """Testing get an order by GET-request from redis cache."""
    test_json = test_data["TEST_BODY_FOR_USER1"].copy()
    if "password" in test_json.keys():
        test_json["passhash"] = hash(test_json.pop("password"))
    else:
        test_json["passhash"] = hash("dsfdsgeregfgf5")
    expected_user, expected_order = None, None

    async with async_session_maker() as async_session:
        query = select(User)
        query = query.filter_by(email=test_json["email"])
        expected_user = await async_session.execute(query)
        expected_user = expected_user.scalars().first()

        if expected_user is None:
            # If there are not any users in database then create it
            expected_user = await model_factory.create(
                model_class=User,
                **test_json
            )

            # TODO: Create order in database for tests
            query2 = select(Order)
            query2 = query2.filter_by(user_id=expected_user.id)
            expected_order = await async_session.execute(query2)
            expected_order = expected_order.scalars().first()

            if expected_order is None:
                # If there are not any orders in database then create it
                time_offset = randint(7, 30)
                order_datetime = datetime.now().astimezone() + timedelta(days=time_offset)
                order_date = date(
                    order_datetime.year, 
                    order_datetime.month, 
                    order_datetime.day
                )
                order_data = {
                    "user_id": expected_user.id, 
                    "order_date": order_date, 
                    "status": "New"
                }
                expected_order = await model_factory.create(
                    model_class=Order, 
                    **order_data
                )
                order_data["order_date"] = order_data["order_date"].strftime("%Y-%m-%d")

    # First request - should go to database and populate cache
    response1 = await client.get(f"/order/{expected_order.id}")
    assert response1.status_code == 200
    
    # Delete from database to ensure next request comes from cache
    async with async_session_maker() as session:
        await model_factory.delete(session, expected_order)
        query = select(Order).where(Order.user_id == expected_user.id)
        checked_order = await async_session.execute(query)
        checked_order = checked_order.scalars().first()
        assert checked_order is None
    
    # Second request - should come from cache
    response2 = await client.get(f"/order/{expected_order.id}")
    assert response2.status_code == 200
    logger.debug(f"Response2: {response2.json()}")
    
    # Verify cached data matches the original response
    response1_data = response1.json()
    response2_data = response2.json()
    
    # Remove dynamic fields that might change between requests
    for data in [response1_data, response2_data]:
        data.pop('created_at', None)
        data.pop('updated_at', None)
    
    assert response1_data == response2_data, "Cached response should match original response"
    
    # Clean up cache
    cache_key = f"order:{expected_order.id}"
    await cache.delete(cache_key)

    async with async_session_maker() as session:
        await session.delete(expected_user)
        await session.commit()
        

@pytest.mark.order
@pytest.mark.asyncio(scope="session")
async def test_update_order(client, async_session_maker, model_factory, test_data):
    """Testing update an order by PATCH-request."""
    test_user = test_data["TEST_BODY_FOR_USER2"]
    async with async_session_maker() as async_session:
        query = delete(User)
        query = query.filter_by(email=test_user["email"])
        await async_session.execute(query)
        await async_session.commit()

    if "passhash" not in test_user.keys():
        if "password" in test_user.keys():
            test_user["passhash"] = hash(test_user.pop("password"))
        else:
            test_user["passhash"] = hash("sdfwegewbegrefr")

    user = await model_factory.create(model_class=User, **test_user)

    time_offset = randint(7, 30)
    order_datetime = datetime.now().astimezone() + timedelta(days=time_offset)
    order_date = date(order_datetime.year, order_datetime.month, order_datetime.day)

    order_data = {"user_id": user.id, "order_date": order_date, "status": "New"}
    order = await model_factory.create(model_class=Order, **order_data)

    data_for_update = {"status": "In Progress"}
    response = await client.patch(f"/order/{order.id}", json=data_for_update)
    response_body = response.json()
    assert response.status_code == 201

    # Проверяем обновленные данные в БД
    async with async_session_maker() as async_session:
        updated_order = await async_session.execute(
            select(Order).
            where(Order.id == order.id)
        )
        updated_order = updated_order.scalars().first()
        updated_order = await updated_order.to_dict()
        
        # Проверяем обновленные поля
        for key in (k for k in updated_order.keys() if k in data_for_update.keys()):
            assert updated_order[key] == data_for_update[key]
        
        # Проверяем, что другие поля не изменились
        non_updated_keys = set(order_data.keys()) - set(data_for_update.keys())
        for key in (k for k in data_for_update.keys() if k in non_updated_keys):
            assert updated_order[key] == order_data[key]

    async with async_session_maker() as async_session:
        await model_factory.delete(async_session, order)
        await model_factory.delete(async_session, user)


@pytest.mark.order
@pytest.mark.asyncio(scope="session")
async def test_delete_order(client, model_factory, async_session_maker, test_data):
    """Testing deleting of an order by DELETE-request."""
    # Тестовые данные
    test_user = test_data["TEST_BODY_FOR_USER1"].copy()        # для создания юзера

    async with async_session_maker() as async_session:
        query = delete(User)
        query = query.filter_by(email=test_user["email"])
        await async_session.execute(query)
        await async_session.commit()

    if password := test_user.pop("password", None):
        test_user["passhash"] = hash(password)
    else:
        test_user["passhash"] = hash("fasdofkn3rjj3k3j2k")

    user = await model_factory.create(model_class=User, **test_user)

    time_offset = randint(7, 30)
    order_datetime = datetime.now().astimezone() + timedelta(days=time_offset)
    order_date = date(order_datetime.year, order_datetime.month, order_datetime.day)

    order_data = {"user_id": user.id, "order_date": order_date, "status": "New"}
    order = await model_factory.create(model_class=Order, **order_data)
    order_id = order.id

    response = await client.delete(f"order/{order_id}")
    assert response.status_code == 200

    async with async_session_maker() as async_session:
        deleted_order = await async_session.execute(
            select(Order).
            where(Order.id == order_id)
        )
        assert deleted_order.scalars().first() is None
        
        await model_factory.delete(async_session, user)