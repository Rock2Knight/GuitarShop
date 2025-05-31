from fastapi import APIRouter, Response, status, HTTPException
from access.base_access import access_model
from dto.guitar import GuitarDto
from loaders.guitar import GuitarLoader

guitar_router = APIRouter(prefix="/guitar", tags=["Гитары"])

@guitar_router.get("/{id}")
async def get_guitar(id: int, response: Response):

    guitar_dump = {'method': 'get', 'id': id}
    guitar_resp = await access_model(loader_class=GuitarLoader, **guitar_dump)
    
    if isinstance(guitar_resp, dict):
        return guitar_resp
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return guitar_resp     # Если возникла ошибка


@guitar_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_guitar(guitar_dto: GuitarDto.Create):

    guitar_dump = {'method': 'post', 'dto': guitar_dto.model_dump()}
    return await access_model(loader_class=GuitarLoader, **guitar_dump)


@guitar_router.patch("/{id}")
async def patch_guitar(id: int, guitar_dto: GuitarDto.Update, response: Response):

    guitar_dump = {'method': 'patch', 'id': id, 'dto': guitar_dto.model_dump()}
    guitar_resp = await access_model(loader_class=GuitarLoader, **guitar_dump)
    if isinstance(guitar_resp, HTTPException):
        response.status_code = guitar_resp.status_code
        return HTTPException(status_code=guitar_resp.status_code)
    response.status_code = status.HTTP_201_CREATED
    return guitar_resp
    

@guitar_router.delete("/{id}")
async def delete_guitar(id: int, response: Response):

    guitar_dump = {'method': 'delete', 'id': id}
    guitar_resp = await access_model(loader_class=GuitarLoader, **guitar_dump)
    if isinstance(guitar_resp, HTTPException):
        response.status_code = guitar_resp.status_code
    return guitar_resp     # Если возникла ошибка