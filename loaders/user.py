from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from loguru import logger

from database import connection
from models import User, Cart
from loaders.model_loader import ModelLoader

class UserLoader(ModelLoader):
    model: User = User

    @classmethod
    @connection
    async def create(cls, session: AsyncSession, **kwargs) -> User:
        passhash = hash(kwargs['password'])  # Находим хэш для пароля
        user = User(email=kwargs['email'],
                    passhash=passhash,
                    username=kwargs['username'])
        
        logger.info(f"email={user.email}, email type = {type(user.email)}\n"
                    f"passhash={user.passhash}, passhash type = {type(user.passhash)}\n"
                    f"username={user.username}, username type = {type(user.username)}")
        
        session.add(user)
        await session.flush()

        cart = Cart(user_id=user.id)
        session.add(cart)
        await session.commit()

        return user
    

    @classmethod
    async def update(cls, user_id: int, **kwargs) -> User:
        if 'password' in kwargs:
            kwargs['passhash'] = hash(kwargs.pop('password'))

            async with async_sessionmaker() as session:
                try:
                    query = select(User).all()
                    users = await session.execute(query).scalars().all()
                    for user in users:
                        if user.passhash == kwargs['passhash']:
                            raise ValueError(f'Пользователь с таким паролем уже существует')
                except Exception as e:
                    await session.rollback()
                    raise e
                finally:
                    await session.close()
            
        
        return await ModelLoader.update(item_id=user_id, **kwargs)