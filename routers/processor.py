from fastapi import APIRouter, Response, status, HTTPException
from access.base_access import access_model
from dto.processor import ProcessorDto
from loaders.processor import ProcessorLoader

processor_router = APIRouter(prefix="/processor", tags=["Гитарные процессоры"])

@processor_router.get("/{id}")
async def get_processor(id: int, response: Response):

    processor_dump = {'method': 'get', 'id': id}
    processor_resp = await access_model(loader_class=ProcessorLoader, **processor_dump)
    
    if isinstance(processor_resp, dict):
        return processor_resp
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return processor_resp     # Если возникла ошибка


@processor_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_processor(processor_dto: ProcessorDto.Create):

    processor_dump = {'method': 'post', 'dto': processor_dto.model_dump()}
    return await access_model(loader_class=ProcessorLoader, **processor_dump)


@processor_router.patch("/{id}")
async def patch_processor(processor_dto: ProcessorDto.Update, response: Response):

    processor_dump = {'method': 'patch', 'guitar_id': id, 'dto': processor_dto.model_dump()}
    processor_resp = await access_model(loader_class=ProcessorLoader, **processor_dump)
    if isinstance(processor_resp, HTTPException):
        response.status_code = processor_resp.status_code
        return HTTPException(status_code=processor_resp.status_code)
    response.status_code = status.HTTP_201_CREATED
    return processor_resp
    

@processor_router.delete("/{id}")
async def delete_processor(response: Response):

    processor_dump = {'method': 'delete', 'id': id}
    processor_resp = await access_model(loader_class=ProcessorLoader, **processor_dump)
    if isinstance(processor_resp, HTTPException):
        response.status_code = processor_resp.status_code
    return processor_resp     # Если возникла ошибка