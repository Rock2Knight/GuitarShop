import asyncpg
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Annotated
from functools import wraps
from sqlalchemy import Integer, func
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column, class_mapper
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from app.config import settings

DATABASE_URL = settings.get_db_url()

# Создаем асинхронный движок для работы с базой данных
engine = create_async_engine(url=DATABASE_URL)
# Создаем фабрику сессий для взаимодействия с базой данных
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

uniq_str_an = Annotated[str, mapped_column(nullable=False, unique=True)]
str_an = Annotated[str, mapped_column(nullable=False)]


# Декоратор для работы с сессией в асинхронных методах
def connection(method):

    @wraps(method)
    async def wrapper(*args, **kwargs):

        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        if 'session' in kwargs.keys():
            kwargs.pop('session')

        async with async_session_maker() as session:
            try:
                return await method(*args, session=session, **kwargs)
            except Exception as e:
                await session.rollback()  # Откатываем сессию при ошибке
                raise e  # Поднимаем исключение дальше
            finally:
                await session.close()  # Закрываем сессию

    return wrapper


# Базовый класс для всех моделей
class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True  # Класс абстрактный, чтобы не создавать отдельную таблицу для него

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    async def to_dict(self) -> dict:
        """Универсальный метод для конвертации объекта SQLAlchemy в словарь"""
        # Получаем маппер для текущей модели
        columns = class_mapper(self.__class__).columns
        # Возвращаем словарь всех колонок и их значений
        return {column.key: getattr(self, column.key) for column in columns}


class Database:
    def __init__(self):
        self.pool = None

    async def init(self):
        self.pool = await asyncpg.create_pool(
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
            host=settings.DB_HOST,
            port=5432,
            min_size=5,      # минимальное соединений в пуле
            max_size=20,     # максимальное соединений в пуле
            max_queries=50000,  # пересоздавать соединение после 50k запросов
            max_inactive_connection_lifetime=300,  # 5 минут неактивности — закрыть
            command_timeout=60  # таймаут на запрос
        )

    async def close(self):
        if self.pool:
            await self.pool.close()

    @asynccontextmanager
    async def acquire(self):
        async with self.pool.acquire() as conn:
            yield conn


db = Database()