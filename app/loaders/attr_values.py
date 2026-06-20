from app.database import db

class AttrValuesLoader:
    
    @staticmethod
    async def get(attr_id: int, product_id: int):
        async with db.acquire() as conn:
            result = await conn.fetchrow(
                """
                SELECT product_id, attribute_id, value
                FROM product_attribute_values
                WHERE attr_id = $1
                AND product_id = $2
                """,
                attr_id, product_id
            )
            return dict(result) if result else None
    

    @staticmethod
    async def get_all_attrs_of_product(product_id: int):
        async with db.acquire() as conn:
            result = await conn.fetch(
                """
                SELECT product_id, attribute_id, value
                FROM product_attribute_values
                WHERE product_id = $1
                """,
                product_id
            )
            return [dict(row) for row in result] if result else []
    
    
    @staticmethod
    async def get_all_values_of_attr(attr_id: int):
        async with db.acquire() as conn:
            result = await conn.fetch(
                """
                SELECT product_id, attribute_id, value
                FROM product_attribute_values
                WHERE attribute_id = $1
                """,
                attr_id
            )
            return [dict(row) for row in result] if result else []

    
    @staticmethod
    async def create_value_of_attr(attr_id: int, product_id: int, value: str):
        async with db.acquire() as conn:
            result = await conn.fetchrow(
                """
                INSERT INTO product_attribute_values (product_id, attribute_id, value)
                VALUES ($1, $2, $3)
                RETURNING product_id, attribute_id, value
                """,
                product_id, attr_id, value
            )
            return dict(result) if result else None
    

    @staticmethod
    async def update_value_of_attr(attr_id: int, product_id: int, new_value: str):
        async with db.acquire() as conn:
            result = await conn.fetchrow(
                """
                UPDATE product_attribute_values
                SET value = $3
                WHERE attribute_id = $1
                AND product_id = $2
                RETURNING product_id, attribute_id, value
                """,
                attr_id, product_id, new_value
            )
            return dict(result) if result else None


    @staticmethod
    async def delete_value_of_attr(attr_id: int, product_id: int):
        async with db.acquire() as conn:
            result = await conn.fetchrow(
                """
                DELETE FROM product_attribute_values
                WHERE attribute_id = $1
                AND product_id = $2
                RETURNING product_id, attribute_id, value
                """,
                attr_id, product_id
            )
            return dict(result) if result else None