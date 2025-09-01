"""Base module for testing http-methods of cart elements"""
from typing import Type, TypeVar, Any
from random import randint

import pytest
from sqlalchemy import select, delete

from app.models import User, Guitar, ComboAmplifier, Cart, CartProduct, ModelClass
from app.logger import logger
from app.cache.redis import cache


@pytest.mark.cart_product
@pytest.mark.asyncio(scope="session")
async def test_get_cart_product(client, async_session_maker, model_factory, removed_keys, test_data):
    """Testing get an cart product by id."""
    test_json_user = test_data["FIRST_EXPECTED_USER"]                  # тестовые данные для юзера
    test_json_cart_product = dict()                                    # тестовые данные для элемента корзины
    test_guitar = test_data["TEST_BODY_FOR_CREATED_GUITAR"]

    # Удаляем пользователя (каскадно удаляется его корзина и все ее элементы)
    async with async_session_maker() as async_session:
        query = delete(User)
        query = query.filter_by(email=test_json_user["email"])
        await async_session.execute(query)
        await async_session.commit()

        query = delete(Guitar)
        query = query.filter_by(name=test_guitar["name"])
        await async_session.execute(query)
        await async_session.commit()

    guitar = await model_factory.create(model_class=Guitar, **test_guitar)
    test_json_cart_product["guitar_id"] = guitar.id

    response = await client.post(f"/user/", json=test_json_user) # создаем нового юзера
    response_body = response.json()
    logger.debug(f"Созданный юзер: {response_body}")
    new_cp = None

    # получаем объект юзера с id
    async with async_session_maker() as async_session:
        query = select(User).filter_by(id=response_body["id"])
        created_user = await async_session.execute(query)
        await async_session.commit()
        created_user = created_user.scalars().first()
        
        assert created_user.cart is not None  # проверяем, что создалась корзина
        test_json_cart_product["cart_id"] = created_user.cart.id
        test_json_cart_product["quantity"] = randint(1, guitar.quantity // 2)

        new_cp = await model_factory.create(
            model_class=CartProduct,
            **test_json_cart_product
        )
        logger.debug(f"Created cart product: {new_cp}")

    response1 = await client.get(f"/cart_product/{new_cp.id}")
    #logger.debug(f"Response body::{cls.product}: {response_body}")
    assert response1.status_code in (200, 201)
    response_body1 = response1.json()

    test_json_cart_product["combo_id"] = None
    test_json_cart_product["processor_id"] = None
    test_json_cart_product["effect_id"] = None

    response_body1 = {k: v for k, v in response_body1.items() if k not in removed_keys}
    assert response_body1 == test_json_cart_product
    new_cp_id = new_cp.id

    async with async_session_maker() as async_session:
        await async_session.delete(new_cp)
        await async_session.commit()
        await async_session.delete(guitar)
        await async_session.commit()
        check_query = select(CartProduct).where(CartProduct.id == new_cp_id)
        check_result = await async_session.execute(check_query)
        check_result = check_result.scalars().first()
        assert check_result is None

    response2 = await client.get(f"/cart_product/{new_cp_id}")
    assert response2.status_code in (200, 201)
    response_body2 = response2.json()
    response_body2 = {k: v for k, v in response_body2.items() if k not in removed_keys}
    assert response_body2 == response_body1

    # Clean up cache
    cache_key = f"cart_product:{new_cp_id}"
    await cache.delete(cache_key)


@pytest.mark.cart_product
@pytest.mark.asyncio(scope="session")
async def test_create_cart_product(client, async_session_maker, model_factory, test_data):
    """Testing create a cart product by POST-request."""
    test_json_user = test_data["TEST_BODY_FOR_USER1"]
    test_json_cart_product = dict()
    test_guitar =  test_data["TEST_BODY_FOR_CREATED_GUITAR"]

    # Удаляем пользователя вместе с корзиной
    async with async_session_maker() as async_session:
        query = delete(User)
        query = query.filter_by(email=test_json_user["email"])
        await async_session.execute(query)
        await async_session.commit()

        query  = delete(Guitar)
        query = query.filter_by(name=test_guitar["name"])
        await async_session.execute(query)
        await async_session.commit()

    guitar = await model_factory.create(
        model_class=Guitar,
        **test_guitar
    )
    test_json_cart_product["guitar_id"] = guitar.id

    response = await client.post(f"/user/", json=test_json_user) # заново создаем юзера
    response_body = response.json()
    cart_product = None
    cart_id = None

    # достаем id корзины из пользователя
    async with async_session_maker() as async_session:
        query = select(User).filter_by(id=response_body["id"])
        created_user = await async_session.execute(query)
        created_user = created_user.scalars().first()
        assert created_user.cart is not None
        test_json_cart_product["cart_id"] = created_user.cart.id
        test_json_cart_product["quantity"] = randint(1, guitar.quantity // 2)
    
    # создаем новый элемент корзины
    response = await client.post(f"/cart_product/", json=test_json_cart_product) 
    response_body = response.json()
    #logger.debug(f"Response = {response_body}")
    assert response.status_code == 201

    # достаем элемент корзины из базы
    async with async_session_maker() as async_session:
        query = select(CartProduct).filter_by(id=response_body["id"])
        cart_product = await async_session.execute(query)
        cart_product = cart_product.scalars().first()
        cart_id = cart_product.cart_id
        cart_product = await cart_product.to_dict()

    for key in (k for k in cart_product.keys() if k in test_json_cart_product.keys()):
        logger.debug(f"cart_product [{key}]: {cart_product.get(key)}")
        logger.debug(f"test_json_cart_product [{key}]: {test_json_cart_product.get(key)}\n")
        assert cart_product.get(key) == test_json_cart_product.get(key)

    async with async_session_maker() as async_session:
        await model_factory.delete(async_session, guitar)


@pytest.mark.cart_product
@pytest.mark.asyncio(scope="session")
async def test_update_cart_product(client, model_factory, async_session_maker, test_data):
    """Testing partial update of an cart product by PATCH-request."""
    # Тестовые данные
    test_json_user_create = test_data["TEST_BODY_FOR_USER1"]        # для создания юзера
    test_guitar = test_data["TEST_BODY_FOR_CREATED_GUITAR"]
    test_combo = test_data["TEST_BODY_FOR_COMBO_AMPLIFIER"]
    test_json_cp_create = dict()                                   # для создания элемента корзины
    test_json_cp_update = dict()                                   # для обновления элемента корзины

    async with async_session_maker() as async_session:
        query = delete(User)
        query = query.filter_by(email=test_json_user_create["email"])
        await async_session.execute(query)
        await async_session.commit()

        query  = delete(Guitar)
        query = query.filter_by(name=test_guitar["name"])
        await async_session.execute(query)
        await async_session.commit()

        query  = delete(ComboAmplifier)
        query = query.filter_by(name=test_combo["name"])
        await async_session.execute(query)
        await async_session.commit()

    response = await client.post(f"/user/", json=test_json_user_create)
    response_body = response.json()
    created_user = None
    cart_product = None

    guitar = await model_factory.create(
        model_class=Guitar,
        **test_guitar
    )
    combo_box = await model_factory.create(
        model_class=ComboAmplifier,
        **test_combo
    )
    test_json_cp_create["guitar_id"] = guitar.id
    test_json_cp_create["quantity"] = randint(1, guitar.quantity // 2)
    test_json_cp_update["combo_id"] = combo_box.id
    test_json_cp_update["quantity"] = randint(1, combo_box.quantity // 2)

    async with async_session_maker() as async_session:
        query = select(User).filter_by(id=response_body["id"])
        created_user = await async_session.execute(query)
        created_user = created_user.scalars().first()
        assert created_user.cart is not None
        test_json_cp_create["cart_id"] = created_user.cart.id

    cart_product = await model_factory.create(
        model_class=CartProduct,
        **test_json_cp_create
    )

    response = await client.patch(
        f"/cart_product/{cart_product.id}",
        json=test_json_cp_update
    )
    response_body = response.json()
    logger.debug(f"Response: {response_body}")
    assert response.status_code == 201

    test_json_cp_update["guitar_id"] = None
    
    # Проверяем обновленные данные в БД
    async with async_session_maker() as async_session:
        updated_cp = await async_session.execute(
            select(CartProduct).
            where(CartProduct.id == cart_product.id)
        )
        updated_cp = updated_cp.scalars().first()
        updated_cp = await updated_cp.to_dict()
        
        # Проверяем обновленные поля
        for key in (k for k in updated_cp.keys() if k in test_json_cp_update.keys()):
            assert updated_cp[key] == test_json_cp_update[key]
        
        # Проверяем, что другие поля не изменились
        non_updated_keys = set(test_json_cp_create.keys()) - set(test_json_cp_update.keys())
        for key in (k for k in updated_cp.keys() if k in non_updated_keys):
            logger.debug(f"updated_cp [{key}]: {updated_cp.get(key)}")
            logger.debug(f"test_json_cp_create [{key}]: {test_json_cp_create.get(key)}\n")
            assert updated_cp[key] == test_json_cp_create[key]

    async with async_session_maker() as async_session:
        await model_factory.delete(async_session, cart_product)
        await model_factory.delete(async_session, guitar)
        await model_factory.delete(async_session, combo_box)


@pytest.mark.cart_product
@pytest.mark.asyncio(scope="session")
async def test_delete_cart_product(client, model_factory, async_session_maker, test_data):
    """Testing deleting of an cart product by DELETE-request."""
    # Тестовые данные
    test_json_user_create = test_data["TEST_BODY_FOR_USER1"]        # для создания юзера
    test_guitar = test_data["TEST_BODY_FOR_CREATED_GUITAR"]
    #test_combo = test_data["TEST_BODY_FOR_COMBO_AMPLIFIER"]

    async with async_session_maker() as async_session:
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
    
    test_data_for_cart = {"user_id": user_id}           # создаем тестовые данные
    created_user.cart = await model_factory.create(
        model_class=Cart,
        **test_data_for_cart
    )

    bound_cart_id = created_user.cart.id
    test_data_for_cart_product = {"cart_id": bound_cart_id}

    guitar = await model_factory.create(
        model_class=Guitar,
        **test_guitar
    )
    test_data_for_cart_product["guitar_id"] = guitar.id
    test_data_for_cart_product["quantity"] = randint(1, guitar.quantity // 2)

    cart_product = await model_factory.create(
        model_class=CartProduct,
        **test_data_for_cart_product
    )
    cart_product_id = cart_product.id

    response = await client.delete(f"cart_product/{cart_product_id}")
    assert response.status_code == 200

    async with async_session_maker() as async_session:
        deleted_cart_product = await async_session.execute(
            select(CartProduct).
            where(CartProduct.id == cart_product_id)
        )
        assert deleted_cart_product.scalars().first() is None
        await model_factory.delete(async_session, cart_product)
        await model_factory.delete(async_session, created_user)
        await model_factory.delete(async_session, guitar)