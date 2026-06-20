from app.database import db

class ProductCategoriesLoader:
    
    @staticmethod
    async def get_all_categories_of_product(product_id):
        async with db.acquire() as conn:
            result = await conn.fetch(
                """
                SELECT category_id
                FROM product_categories
                WHERE product_id = $1
                """,
                product_id
            )
            return [row["category_id"] for row in result] if result else []
    

    @staticmethod
    async def get_all_products_of_category(category_id: int):
        async with db.acquire() as conn:
            result = await conn.fetch(
                """
                SELECT product_id
                FROM product_categories
                WHERE category_id = $1
                """,
                category_id
            )
            return [row["product_id"] for row in result] if result else []
    
    @staticmethod
    async def create_relation(product_id: int, category_id: int):
        async with db.acquire() as conn:
            result = await conn.fetchrow(
                """
                INSERT INTO product_categories (product_id, category_id)
                VALUES ($1, $2)
                RETURNING product_id, category_id
                """,
                product_id, category_id
            )
            return dict(result) if result else None


    @staticmethod
    async def delete_relation(product_id: int, category_id: int):
        async with db.acquire() as conn:
            result = await conn.fetchrow(
                """
                DELETE FROM product_categories
                WHERE product_id = $1
                AND category_id = $2
                RETURNING product_id, category_id
                """,
                product_id, category_id
            )
            return dict(result) if result else None