from fastapi import APIRouter, Response, status, HTTPException
from access.base_access import access_model
from dto.combo_ampf import ComboAmpfDto
from loaders.combo_ampf import ComboAmpfLoader

combo_router = APIRouter(prefix="/combo_ampf", tags=["Комбо-усилители"])

@combo_router.get("/{id}")
async def get_combo(id: int, response: Response):

    combo_dump = {'method': 'get', 'id': id}
    combo_resp = await access_model(loader_class=ComboAmpfLoader, **combo_dump)
    
    if isinstance(combo_resp, dict):
        return combo_resp
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return combo_resp     # Если возникла ошибка


@combo_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_combo(combo_dto: ComboAmpfDto.Create):

    combo_dump = {'method': 'post', 'dto': combo_dto.model_dump()}
    return await access_model(loader_class=ComboAmpfLoader, **combo_dump)


@combo_router.patch("/{id}")
async def patch_combo(id: int, combo_dto: ComboAmpfDto.Update, response: Response):

    combo_dump = {'method': 'patch', 'id': id, 'dto': combo_dto.model_dump()}
    combo_resp = await access_model(loader_class=ComboAmpfLoader, **combo_dump)
    if isinstance(combo_resp, HTTPException):
        response.status_code = combo_resp.status_code
        return HTTPException(status_code=combo_resp.status_code)
    response.status_code = status.HTTP_201_CREATED
    return combo_resp
    

@combo_router.delete("/{id}")
async def delete_combo(id: int, response: Response):

    combo_dump = {'method': 'delete', 'id': id}
    combo_resp = await access_model(loader_class=ComboAmpfLoader, **combo_dump)
    if isinstance(combo_resp, HTTPException):
        response.status_code = combo_resp.status_code
    return combo_resp     # Если возникла ошибка