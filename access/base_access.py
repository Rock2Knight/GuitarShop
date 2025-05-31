from typing import Optional, Type, TypeVar

from fastapi import HTTPException, status

from database import Base

T = TypeVar('T', bound=Base)  # Generic тип для модели

async def access_model(
    loader_class: Type,  # Класс загрузчика (GuitarLoader, ProcessorLoader и т.д.)
    **kwargs
) -> Optional[dict | HTTPException]:
    """
    Базовый обработчик CRUD-операций для моделей
    
    Args:
        loader_class: Класс загрузчика, наследованный от BaseLoader
        **kwargs:
            - method: get/post/patch/delete
            - id: ID объекта (для get/patch/delete)
            - dto: Данные для создания/обновления (для post/patch)
            
    Returns:
        Словарь с данными объекта или HTTPException при ошибке
    """
    try:
        match kwargs['method']:
            case "get":
                item = await loader_class.get(item_id=kwargs['id'])
                if not item:
                    return HTTPException(status_code=status.HTTP_404_NOT_FOUND)
                return await item.to_dict()
                
            case "post":
                item = await loader_class.create(**kwargs['dto'])
                return await item.to_dict()
                
            case "patch":
                item = await loader_class.update(
                    item_id=kwargs['id'],
                    **kwargs['dto']
                )
                if not item:
                    return HTTPException(status_code=status.HTTP_404_NOT_FOUND)
                return await item.to_dict()
                
            case "delete":
                item_dict = await loader_class.delete(item_id=kwargs['id'])
                return item_dict
                
    except ValueError as e:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )