from app.database import db

class CategoryAttrsLoader:
    
    @staticmethod
    async def get_all_attrs_of_category(category_id):
        async with db.acquire() as conn:
            result = await conn.fetch(
                """
                SELECT attribute_id
                FROM category_attributes
                WHERE category_id = $1
                """,
                category_id
            )
            return [row["attribute_id"] for row in result] if result else []
    

    @staticmethod
    async def get_all_categories_of_attr(attr_id: int):
        async with db.acquire() as conn:
            result = await conn.fetch(
                """
                SELECT category_id
                FROM category_attributes
                WHERE attribute_id = $1
                """,
                attr_id
            )
            return [row["category_id"] for row in result] if result else []
    
    @staticmethod
    async def create_relation(category_id: int, attr_id: int):
        async with db.acquire() as conn:
            result = await conn.fetchrow(
                """
                INSERT INTO category_attributes (category_id, attribute_id)
                VALUES ($1, $2)
                RETURNING category_id, attribute_id
                """,
                category_id, attr_id
            )
            return dict(result) if result else None


    @staticmethod
    async def delete_relation(category_id: int, attr_id: int):
        async with db.acquire() as conn:
            result = await conn.fetchrow(
                """
                DELETE FROM category_attributes
                WHERE category_id = $1
                AND attribute_id = $2
                RETURNING category_id, attribute_id
                """,
                category_id, attr_id
            )
            return dict(result) if result else None