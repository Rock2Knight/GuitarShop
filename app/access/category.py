from typing import Optional

from fastapi import HTTPException, status

from app.access.base_access import access_model
from app.loaders.attributes import AttributesLoader
from app.loaders.category import CategoryLoader
from app.loaders.category_attrs import CategoryAttrsLoader

async def access_category(**kwargs) -> Optional[dict[str, str] | HTTPException]:
    if kwargs['method'] == 'get':
        try:
            # 1. Получаем саму категорию
            category = await CategoryLoader.get_category_by_name(category_name=kwargs['name'])
            if not category:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category with such id not found")

            # 2. Достаем все атрибуты категории
            attrs_ids = await CategoryAttrsLoader.get_all_attrs_of_category(category.id)
            attrs = [await AttributesLoader.get(item_id=attr_id) for attr_id in attrs_ids]
            attrs = [dict(id=attr.id, name=attr.name) for attr in attrs]
            
            # 3. Фомрируем итоговый результат
            res = {
                "category_id": category.id,
                "category_name": category.name,
                "attributes": attrs
            }
            return res

        except Exception as e:
            if isinstance(e, HTTPException):
                return e
            return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    elif kwargs['method'] == 'post':
        try:
            attrs = kwargs['dto'].pop("attributes")

            if "parent_category_name" in kwargs['dto']:
                lol = kwargs['dto'].pop("parent_category_name")
                parent_category = await CategoryLoader.get_category_by_name(category_name=lol)
                if not parent_category:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, 
                        detail="Parent category with such name not found"
                    )
                kwargs['dto']['parent_id'] = parent_category.id

            category = await CategoryLoader.create(**kwargs['dto'])

            attr_dict = {}
            for attr in attrs:
                # 1. Сначала проверяем, что атрибут с таким именем еще не существует
                existing_attr = await AttributesLoader.get_attribute_by_name(name=attr)
                if existing_attr is None:
                    # 2. Если атрибут не существует, создаем его
                    existing_attr = await AttributesLoader.create(name=attr)
                    
                attr_dict[existing_attr.id] = existing_attr.name
                # 3. Создаем связь между аттрибутом и категорией
                await CategoryAttrsLoader.create_relation(category_id=category.id, attr_id=existing_attr.id)

            res = {
                "category_id": category.id,
                "category_name": category.name,
                "attributes": attr_dict
            }

            if "parent_category_name" in kwargs['dto']:
                res["parent_category"] = {
                    "parent_id": parent_category.id,
                    "parent_name": parent_category.name
                }
                
            return res

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.args)


    elif kwargs['method'] == 'patch':
        try:
            attrs = kwargs['dto'].pop("attributes")
            category = await CategoryLoader.update(item_id=kwargs['id'], **kwargs['dto'])

            changed_attrs = dict()
            for attr in attrs:
                attr_obj = await AttributesLoader.get_attribute_by_name(name=attr)
                if not attr_obj:
                    attr_obj = await AttributesLoader.create(name=attr)
                    
                changed_attr_id = await CategoryAttrsLoader.create_relation(category_id=category.id, attr_id=attr_obj.id)
                changed_attrs[changed_attr_id.get("attribute_id")] = attr_obj.name

            res = {
                "category_id": category.id,
                "category_name": category.name,
                "attributes": changed_attrs
            }
                
            return res

        except Exception as e:
            return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.args)

    else:
        return await access_model(loader_class=CategoryLoader, **kwargs)