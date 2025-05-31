from typing import Optional

from fastapi import HTTPException, status

from dto.guitar import GuitarDto
from loaders.guitar import GuitarLoader
from models import Guitar


async def access_guitar(**kwargs) -> Optional[Guitar | HTTPException]:
    match kwargs['method']:
        case "get":
            try:
                guitar = await GuitarLoader.get(guitar_id=kwargs['id'])
                return await guitar.to_dict()
            except Exception as e:
                return HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        case "post":
            try:
                guitar = await GuitarLoader.create(**kwargs['dto'])
                return await guitar.to_dict()
            except Exception:
                return HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        case 'patch':
            try:
                id = kwargs.pop('id')
                guitar = await GuitarLoader.update(guitar_id=id, **kwargs['dto'])
                return await guitar.to_dict()
            except Exception:
                return HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        case "delete":
            try:
                guitar = GuitarLoader.delete(guitar_id=kwargs['id'])
                return await guitar.to_dict()
            except Exception:
                return HTTPException(status_code=status.HTTP_400_BAD_REQUEST)