from typing import override

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.logger import logger

from app.database import connection
from app.models import User, Cart
from app.loaders.model_loader import ModelLoader

class UserLoader(ModelLoader[User]):
    model: User = User

    @classmethod
    @override
    @connection
    async def create(cls, session: AsyncSession, **kwargs) -> User:
        passhash = hash(kwargs['password'])  # Находим хэш для пароля
        user = User(
            email=kwargs['email'],
            passhash=passhash,
            username=kwargs['username'],
            cart=Cart()
        )
        
        session.add(user)
        try:
            await session.commit()
            await session.refresh(user)
        except Exception as e:
            await session.rollback()
            raise e

        return user
    

    @classmethod
    @override
    @connection
    async def update(cls, session: AsyncSession, user_id: int, **kwargs) -> User:
        if 'password' in kwargs:
            
            kwargs['passhash'] = hash(kwargs.pop('password'))
            try:
                query = select(User).all()
                users = await session.execute(query).scalars().all()
                for user in users:
                    if user.passhash == kwargs['passhash']:
                        raise ValueError(f'Пользователь с таким паролем уже существует')
            except Exception as e:
                await session.rollback()
                raise e
        
        query = select(cls.model).filter_by(id=user_id)
        user = await session.scalars(query)

        if not user:
            return None
        
        user = user.first()
        if not user:
            return None

        for key, value in kwargs.items():
            setattr(user, key, value)

        try:    
            await session.commit()
            await session.refresh(user)
        except Exception as e:
            await session.rollback()
            raise e
        return user