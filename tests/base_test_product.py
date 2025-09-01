"""Base module for testing http-methods of products"""
from typing import Type, TypeVar, Any
import json

import pytest
from sqlalchemy import select, delete

from app.models import Product
from app.logger import logger
from app.cache.redis import cache

ProductModel = TypeVar("ProductModel", bound=Product)

class BaseTestProduct:
    """Interface for testing http-mehods of product models."""

    product: Type[ProductModel]  # Модель SQLAlchemy (например, Guitar)
    endpoint_prefix: str  # Префикс эндпоинта (например, "/guitars")
    test_data: dict[str, Any]  # Пример данных для создания/обновления

    @classmethod
    @pytest.mark.asyncio(scope="session")
    async def test_get(cls, client, async_session_maker, model_factory, removed_keys):
        """Testing get a product by id."""
        test_json = cls.test_data["FIRST_EXPECTED"]
        description = test_json.pop("description")

        async with async_session_maker() as async_session:
            query = delete(cls.product)
            query = query.filter_by(name=test_json["name"])
            await async_session.execute(query)
            await async_session.commit()

        expected_product = await model_factory.create(
            model_class=cls.product,
            **test_json
        )

        response = await client.get(f"{cls.endpoint_prefix}/{expected_product.id}")
        response_body = response.json()
        logger.debug(f"Response body::{cls.product}: {response_body}")
        assert response.status_code in (200, 201)

        test_json["description"] = description
        response_body = response.json()
        response_body = {k: v for k, v in response_body.items() if k not in removed_keys}
        assert response_body == test_json
        
        # Verify data was cached
        cache_key = f"{cls.product.__tablename__}:{expected_product.id}" # формируем ключ для Redis
        async with async_session_maker() as async_session:
            await model_factory.delete(async_session, expected_product)
            # Clear the cache after test
            await cache.delete(cache_key)


    @classmethod
    @pytest.mark.asyncio(scope="session")
    async def test_create_product(cls, client, async_session_maker, test_data):
        """Testing create a product by POST-request."""
        test_json = cls.test_data["TEST_BODY"]
        async with async_session_maker() as async_session:
            query = delete(cls.product)
            query = query.filter_by(name=test_json["name"])
            await async_session.execute(query)
            await async_session.commit()

        response = await client.post(f"{cls.endpoint_prefix}/", json=test_json)
        response_body = response.json()

        assert response.status_code == 201

        created_product = None

        async with async_session_maker() as async_session:
            name = response_body["name"]
            created_product = await async_session.execute(
                select(cls.product).where(cls.product.name == name)
            )
            created_product = created_product.scalars().first()
            created_product = await created_product.to_dict()

        for key in (k for k in created_product.keys() if k in test_json.keys()):
            assert created_product.get(key) == test_json.get(key)


    @classmethod
    @pytest.mark.asyncio(scope="session")
    async def test_get_from_cache(cls, client, model_factory, async_session_maker, clear_cache):
        """Test getting data from Redis cache."""
        # Create test data
        test_json = cls.test_data["FIRST_EXPECTED"].copy()
        description = test_json.pop("description")
        expected_product = None
        
        # Здесь проверяем, содержится ли товар с таким именем в базе
        async with async_session_maker() as async_session:
            query = select(cls.product)
            query = query.filter_by(name=test_json["name"])

            # Получаем товар из базы
            expected_product = await async_session.execute(query)
            expected_product = expected_product.scalars().first()

            if expected_product is None:
                # If there are not any products in database then create it
                expected_product = await model_factory.create(
                    model_class=cls.product,
                    **test_json
                ) 
        
        # First request - should go to database and populate cache
        response1 = await client.get(f"{cls.endpoint_prefix}/{expected_product.id}")
        assert response1.status_code == 200
        
        # Delete from database to ensure next request comes from cache
        async with async_session_maker() as session:
            await model_factory.delete(session, expected_product)
        
        # Second request - should come from cache
        response2 = await client.get(f"{cls.endpoint_prefix}/{expected_product.id}")
        assert response2.status_code == 200
        
        # Verify cached data matches the original response
        response1_data = response1.json()
        response2_data = response2.json()
        
        # Remove dynamic fields that might change between requests
        for data in [response1_data, response2_data]:
            data.pop('created_at', None)
            data.pop('updated_at', None)
        
        assert response1_data == response2_data, "Cached response should match original response"
        
        # Clean up cache
        cache_key = f"{cls.product.__tablename__}:{expected_product.id}"
        await cache._redis.delete(cache_key)


    @classmethod
    @pytest.mark.asyncio(scope="session")
    async def test_update_product(cls, client, model_factory, async_session_maker):
        """Testing partial update of a product by PATCH-request."""
        test_json_create = cls.test_data["TEST_BODY"]
        test_json_update = cls.test_data["TEST_UPDATED_DATA"]

        async with async_session_maker() as async_session:
            query = delete(cls.product)
            query = query.filter_by(name=test_json_create["name"])
            await async_session.execute(query)
            await async_session.commit()

        created_product = await model_factory.create(
            model_class=cls.product,
            **test_json_create
        )
        product_id = created_product.id

        response = await client.patch(
            f"{cls.endpoint_prefix}/{product_id}",
            json=test_json_update
        )
        assert response.status_code == 201
        
        # Проверяем обновленные данные в БД
        async with async_session_maker() as async_session:
            updated_product = await async_session.execute(
                select(cls.product).
                where(cls.product.id == product_id)
            )
            updated_product = updated_product.scalars().first()
            updated_product = await updated_product.to_dict()
            
            # Проверяем обновленные поля
            for key in (k for k in updated_product.keys() if k in test_json_update.keys()):
                assert updated_product[key] == test_json_update[key]
            
            # Проверяем, что другие поля не изменились
            non_updated_keys = set(test_json_create.keys()) - set(test_json_update.keys())
            for key in (k for k in updated_product.keys() if k in non_updated_keys):
                assert updated_product[key] == test_json_create[key]

        async with async_session_maker() as async_session:
            await model_factory.delete(async_session, created_product)


    @classmethod
    @pytest.mark.asyncio(scope="session")
    async def test_delete_product(cls, client, model_factory, async_session_maker):
        """Testing deletion of a effect pedal by DELETE-request."""
        test_json = cls.test_data["TEST_BODY"]

        async with async_session_maker() as async_session:
            query = delete(cls.product)
            query = query.filter_by(name=test_json["name"])
            await async_session.execute(query)
            await async_session.commit()

        created_product = await model_factory.create(
            model_class=cls.product,
            **test_json
        )
        product_id = created_product.id

        response = await client.delete(f"{cls.endpoint_prefix}/{product_id}")
        assert response.status_code == 200
        
        async with async_session_maker() as async_session:
            deleted_product = await async_session.execute(
                select(cls.product).
                where(cls.product.id == product_id)
            )
            assert deleted_product.scalars().first() is None