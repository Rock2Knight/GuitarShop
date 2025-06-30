from fastapi import APIRouter, Response, status, HTTPException

from app.access.base_access import access_model
from app.access.user import access_user
from app.dto.user import UserDto
from app.loaders.user import UserLoader

user_router = APIRouter(prefix="/user", tags=["Пользователи"])

@user_router.get("/{id}")
async def get_user(id: int, response: Response):

    user_dump = {'method': 'get', 'id': id}
    user_resp = await access_user(**user_dump)
    
    if isinstance(user_resp, dict):
        response.status_code = status.HTTP_200_OK
        return user_resp
    else:
        response.status_code = 500
        return user_resp     # Если возникла ошибка


@user_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user_dto: UserDto.Create):

    user_dump = {'method': 'post', 'dto': user_dto.model_dump()}
    return await access_user(**user_dump)


@user_router.patch("/{id}")
async def patch_user(id: int, user_dto: UserDto.Update, response: Response):

    user_dump = {'method': 'patch', 'id': id, 'dto': user_dto.model_dump()}
    user_resp = await access_user(**user_dump)
    if isinstance(user_resp, HTTPException):
        response.status_code = user_resp.status_code
        return HTTPException(status_code=user_resp.status_code)
    response.status_code = status.HTTP_201_CREATED
    return user_resp
    

@user_router.delete("/{id}")
async def delete_user(id: int, response: Response):

    user_dump = {'method': 'delete', 'id': id}
    user_resp = await access_model(loader_class=UserLoader, **user_dump)
    if isinstance(user_resp, HTTPException):
        response.status_code = user_resp.status_code
    return user_resp     # Если возникла ошибка