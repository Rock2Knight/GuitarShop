from typing import Optional

from fastapi import HTTPException, status

from dto.processor import ProcessorDto
from loaders.processor import ProcessorLoader
from models import Processor


async def access_processor(**kwargs) -> Optional[Processor | HTTPException]:
    match kwargs['method']:
        case "get":
            try:
                processor = await ProcessorLoader.get(processor_id=kwargs['id'])
                return await processor.to_dict()
            except Exception as e:
                return HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        case "post":
            try:
                processor = await ProcessorLoader.create(**kwargs['dto'])
                return await processor.to_dict()
            except Exception:
                return HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        case 'patch':
            try:
                id = kwargs.pop('id')
                processor = await ProcessorLoader.update(processor_id=id, **kwargs['dto'])
                return await processor.to_dict()
            except Exception:
                return HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        case "delete":
            try:
                processor = ProcessorLoader.delete(processor_id=kwargs['id'])
                return await processor.to_dict()
            except Exception:
                return HTTPException(status_code=status.HTTP_400_BAD_REQUEST)