from typing import Optional

from fastapi import HTTPException, status

from app.loaders.user import UserLoader
from app.loaders.cart import CartLoader
from app.models import User
from app.logger import logger


async def access_user(**kwargs) -> Optional[User | HTTPException]:
    match kwargs['method']:
        case "get":
            try:
                user = await UserLoader.get(item_id=kwargs['id'])
                logger.info(f"Fields of user {user}")
                user_dump = await user.to_dict()
                user_dump.pop('passhash')
                return user_dump
            except Exception as e:
                return HTTPException(status_code=500, detail=e.detail)
        case "post":
            try:
                user = await UserLoader.create(**kwargs['dto'])
                await CartLoader.create(user_id=user.id)
                user_dump = await user.to_dict()
                user_dump.pop('passhash')
                return user_dump
            except Exception as e:
                return HTTPException(status_code=500, detail=e.detail)
        case 'patch':
            try:
                id = kwargs.pop('id')
                user = await UserLoader.update(user_id=id, **kwargs['dto'])
                user_dump = await user.to_dict()
                user_dump.pop('passhash')
                return user_dump
            except Exception as e:
                return HTTPException(status_code=500, detail=e.detail)
        case "delete":
            try:
                user_dump = UserLoader.delete(item_id=kwargs['id'])
                return user_dump
            except Exception as e:
                return HTTPException(status_code=500, detail=e.detail)