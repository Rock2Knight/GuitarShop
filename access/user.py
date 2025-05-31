from typing import Optional

from loguru import logger
from fastapi import HTTPException, status

from dto.user import UserDto
from loaders.user import UserLoader
from models import User


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
                logger.info(f"Exception: {e}")
                return HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        case "post":
            try:
                user = await UserLoader.create(**kwargs['dto'])
                user_dump = await user.to_dict()
                user_dump.pop('passhash')
                return user_dump
            except Exception:
                return HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        case 'patch':
            try:
                id = kwargs.pop('id')
                user = await UserLoader.update(user_id=id, **kwargs['dto'])
                user_dump = await user.to_dict()
                user_dump.pop('passhash')
                return user_dump
            except Exception:
                return HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        case "delete":
            try:
                user_dump = UserLoader.delete(item_id=kwargs['id'])
                return user_dump
            except Exception:
                return HTTPException(status_code=status.HTTP_400_BAD_REQUEST)