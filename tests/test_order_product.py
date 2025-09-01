"""Base module for testing http-methods of order products"""
from random import randint
from datetime import date, datetime, timedelta

import pytest
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from app.models import Guitar, User, Order, OrderProduct, ComboAmplifier
from app.cache.redis import cache

@pytest.mark.order_product
@pytest.mark.asyncio(scope="session")
async def test_get_order_product(
    client, async_session_maker, 
    model_factory, removed_keys, test_data
):
    """Testing get an order product by GET-request."""
    test_user = test_data["TEST_BODY_FOR_USER1"].copy()             # Описание юзера
    test_guitar = test_data["TEST_BODY_FOR_CREATED_GUITAR"].copy()  # тестовая гитара
    
    async with async_session_maker() as async_session:
        """Удаление заказов и пользователей"""
        sel_query = select(User)
        sel_query = sel_query.options(selectinload(User.orders))
        sel_query = sel_query.filter_by(email=test_user["email"])

        user = await async_session.execute(sel_query)
        user = user.scalars().first()
        if user and user.orders:
            for order in user.orders:
                if order.order_products:
                    for op in order.order_products:
                        await async_session.delete(op)
                        await async_session.commit()
                await async_session.delete(order)
                await async_session.commit()

        query = delete(User)
        query = query.filter_by(email=test_user["email"])
        await async_session.execute(query)
        await async_session.commit()

        query = delete(Guitar)
        query = query.filter_by(name=test_guitar["name"])
        await async_session.execute(query)
        await async_session.commit()

    """Вычисляем хэш пароля"""
    if "passhash" not in test_user.keys():
        if "password" in test_user.keys():
            test_user["passhash"] = hash(test_user.pop("password"))
        else:
            test_user["passhash"] = hash("sdfwegewbegrefr")

    user = await model_factory.create(model_class=User, **test_user) # Создаем юзера
    
    # Генерируем срок доставки заказа
    time_offset = randint(7, 30)
    order_datetime = datetime.now().astimezone() + timedelta(days=time_offset)
    order_date = date(order_datetime.year, order_datetime.month, order_datetime.day)

    order_data = {"user_id": user.id, "order_date": order_date, "status": "New"}
    user.order = await model_factory.create(model_class=Order, **order_data)  # Создаем заказ

    guitar = await model_factory.create(model_class=Guitar, **test_guitar)  # Создаем гитару

    # Данные для товара из заказа
    order_product_data = {
        "order_id": user.order.id,
        "guitar_id": guitar.id,
        "quantity": guitar.quantity // 2   
    }

    # Добавляем товар из заказа в базу
    order_product = await model_factory.create(model_class=OrderProduct, **order_product_data)
    order_product_id = order_product.id

    # Получаем товар из заказа с помощью GET-запроса к API
    response1 = await client.get(f"/order_product/{order_product_id}")
    assert response1.status_code in (200, 201)
    response_body1 = response1.json()

    response_body1 = {k: v for k, v in response_body1.items() if k not in removed_keys}
    
    for key in (k for k in order_product_data.keys() if k in response_body1.keys()):
        assert response_body1[key] == order_product_data[key]
    
    async with async_session_maker() as async_session:
        await model_factory.delete(async_session, order_product)
        query_sel = select(OrderProduct).where(OrderProduct.id == order_product_id)
        result = await async_session.execute(query_sel)
        result = result.scalars().first()
        assert result is None

    # Снова делаем GET-запрос к API. В данном случае приложение должно достать данные из Redis
    response2 = await client.get(f"/order_product/{order_product_id}")
    assert response2.status_code in (200, 201)
    response_body2 = response2.json()

    # Remove dynamic fields that might change between requests
    for data in [response_body1, response_body2]:
        data.pop('id', None)
        data.pop('created_at', None)
        data.pop('updated_at', None)
    
    # Проверяем, что данные из базы совпадают с данными из кэша
    assert response_body1 == response_body2, "Cached response should match original response"
    
    # Clean up cache
    cache_key = f"order_product:{order_product_id}"
    await cache.delete(cache_key)

    async with async_session_maker() as session:
        await session.delete(user)
        await session.delete(guitar)
        await session.commit()


@pytest.mark.order_product
@pytest.mark.asyncio(scope="session")
async def test_post_order_product(
    client, async_session_maker, 
    model_factory, removed_keys, test_data
):
    """Testing post an order product by POST-request."""
    test_user = test_data["TEST_BODY_FOR_USER1"]
    test_guitar = test_data["TEST_BODY_FOR_CREATED_GUITAR"]

    async with async_session_maker() as async_session:
        sel_query = select(User)
        sel_query = sel_query.options(selectinload(User.orders))
        sel_query = sel_query.filter_by(email=test_user["email"])

        user = await async_session.execute(sel_query)
        user = user.scalars().first()
        if user and user.orders:
            for order in user.orders:
                if order.order_products:
                    for op in order.order_products:
                        await async_session.delete(op)
                        await async_session.commit()
                await async_session.delete(order)
                await async_session.commit()

        query = delete(User)
        query = query.filter_by(email=test_user["email"])
        await async_session.execute(query)
        await async_session.commit()

        query = delete(Guitar)
        query = query.filter_by(name=test_guitar["name"])
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
    user.order = await model_factory.create(model_class=Order, **order_data)

    guitar = await model_factory.create(model_class=Guitar, **test_guitar)

    order_product_data = {
        "order_id": user.order.id,
        "guitar_id": guitar.id,
        "quantity": guitar.quantity // 2   
    }

    response = await client.post("/order_product/", json=order_product_data)
    response_body = response.json()
    assert response.status_code == 201
    order_product_id = response_body["id"]
    created_op = None

    async with async_session_maker() as async_session:
        created_op = await async_session.execute(
            select(OrderProduct).
            where(OrderProduct.id == order_product_id)
        )
        created_op = created_op.scalars().first()
        created_op = await created_op.to_dict()

    for key in (k for k in created_op.keys() if k in order_product_data.keys()):
        assert created_op.get(key) == order_product_data.get(key)



@pytest.mark.order_product
@pytest.mark.asyncio(scope="session")
async def test_update_order_product(
    client, async_session_maker, 
    model_factory, removed_keys, test_data
):
    """Testing update an order product by PATCH-request."""
    test_user = test_data["TEST_BODY_FOR_USER2"]
    test_guitar = test_data["TEST_BODY_FOR_CREATED_GUITAR"]
    test_combo = test_data["TEST_BODY_FOR_COMBO_AMPLIFIER"]

    async with async_session_maker() as async_session:
        sel_query = select(User)
        sel_query = sel_query.options(selectinload(User.orders))
        sel_query = sel_query.filter_by(email=test_user["email"])

        user = await async_session.execute(sel_query)
        user = user.scalars().first()
        if user and user.orders:
            for order in user.orders:
                if order.order_products:
                    for op in order.order_products:
                        await async_session.delete(op)
                        await async_session.commit()
                await async_session.delete(order)
                await async_session.commit()

        query = delete(User)
        query = query.filter_by(email=test_user["email"])
        await async_session.execute(query)
        await async_session.commit()

        query = delete(Guitar)
        query = query.filter_by(name=test_guitar["name"])
        await async_session.execute(query)
        await async_session.commit()

        query = delete(ComboAmplifier)
        query = query.filter_by(name=test_combo["name"])
        await async_session.execute(query)
        await async_session.commit()

    if "passhash" not in test_user.keys():
        if "password" in test_user.keys():
            test_user["passhash"] = hash(test_user.pop("password"))
        else:
            test_user["passhash"] = hash("fewwefsfdsfsg")

    user = await model_factory.create(model_class=User, **test_user)
    
    time_offset = randint(7, 30)
    order_datetime = datetime.now().astimezone() + timedelta(days=time_offset)
    order_date = date(order_datetime.year, order_datetime.month, order_datetime.day)

    order_data = {"user_id": user.id, "order_date": order_date, "status": "New"}
    user.order = await model_factory.create(model_class=Order, **order_data)

    guitar = await model_factory.create(model_class=Guitar, **test_guitar)
    combo = await model_factory.create(model_class=ComboAmplifier, **test_combo)

    order_product_data = {
        "order_id": user.order.id,
        "guitar_id": guitar.id,
        "quantity": guitar.quantity // 2   
    }

    order_product = await model_factory.create(model_class=OrderProduct, **order_product_data)
    order_product_id = order_product.id

    data_for_update = {"combo_id": combo.id, "quantity": randint(1, combo.quantity // 2)}

    response = await client.patch(f"/order_product/{order_product_id}", json=data_for_update)
    response_body = response.json()
    assert response.status_code == 201

    # Проверяем обновленные данные в БД
    async with async_session_maker() as async_session:
        updated_op = await async_session.execute(
            select(OrderProduct).
            where(OrderProduct.id == order_product_id)
        )
        updated_op = updated_op.scalars().first()
        updated_op = await updated_op.to_dict()
        
        # Проверяем обновленные поля
        for key in (k for k in updated_op.keys() if k in data_for_update.keys()):
            assert updated_op[key] == data_for_update[key]
        
        # Проверяем, что другие поля не изменились
        order_product_data.pop("guitar_id")
        non_updated_keys = set(order_product_data.keys()) - set(data_for_update.keys())
        for key in (k for k in updated_op.keys() if k in non_updated_keys):
            assert updated_op[key] == order_product_data[key]


@pytest.mark.order_product
@pytest.mark.asyncio(scope="session")
async def test_delete_order_product(
    client, model_factory, 
    async_session_maker, test_data
):
    """Testing deleting of an order product by DELETE-request."""
    
    test_json_user_create = test_data["TEST_BODY_FOR_USER1"]        # для создания юзера
    test_guitar = test_data["TEST_BODY_FOR_CREATED_GUITAR"]

    async with async_session_maker() as async_session:
        sel_query = select(User)
        sel_query = sel_query.options(selectinload(User.orders))
        sel_query = sel_query.filter_by(email=test_json_user_create["email"])

        user = await async_session.execute(sel_query)
        user = user.scalars().first()
        if user and user.orders:
            for order in user.orders:
                if order.order_products:
                    for op in order.order_products:
                        await async_session.delete(op)
                        await async_session.commit()
                await async_session.delete(order)
                await async_session.commit()

        query = delete(User)
        query = query.filter_by(email=test_json_user_create["email"])
        await async_session.execute(query)
        await async_session.commit()

        query  = delete(Guitar)
        query = query.filter_by(name=test_guitar["name"])
        await async_session.execute(query)
        await async_session.commit()

    if password := test_json_user_create.pop("password", None):
        test_json_user_create["passhash"] = hash(password)
    else:
        test_json_user_create["passhash"] = hash("fasdofkn3rjj3k3j2k")

    created_user = await model_factory.create(
        model_class=User,
        **test_json_user_create
    )
    user_id = created_user.id

    guitar = await model_factory.create(
        model_class=Guitar,
        **test_guitar
    )

    time_offset = randint(7, 30)
    order_datetime = datetime.now().astimezone() + timedelta(days=time_offset)
    order_date = date(order_datetime.year, order_datetime.month, order_datetime.day)

    order_data = {"user_id": user_id, "order_date": order_date, "status": "New"}
    created_user.order = await model_factory.create(
        model_class=Order, 
        **order_data
    )
    
    test_data_for_op = {
        "order_id": created_user.order.id, 
        "guitar_id": guitar.id,
        "quantity": randint(1, guitar.quantity // 2)
    }           # создаем тестовые данные
    
    order_product = await model_factory.create(
        model_class=OrderProduct,
        **test_data_for_op
    )
    order_product_id = order_product.id

    response = await client.delete(f"order_product/{order_product_id}")
    assert response.status_code == 200

    async with async_session_maker() as async_session:
        deleted_cart_product = await async_session.execute(
            select(OrderProduct).
            where(OrderProduct.id == order_product_id)
        )
        assert deleted_cart_product.scalars().first() is None
        await model_factory.delete(async_session, created_user)
        await model_factory.delete(async_session, guitar)