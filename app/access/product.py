from typing import Optional

from fastapi import HTTPException, status

from app.loaders.product import ProductLoader
from app.loaders.category import CategoryLoader
from app.loaders.attributes import AttributesLoader
from app.loaders.attr_values import AttrValuesLoader
from app.loaders.category_attrs import CategoryAttrsLoader
from app.loaders.product_categories import ProductCategoriesLoader

async def access_product(**kwargs) -> Optional[dict | HTTPException]:
    try:
        match kwargs['method']:
            case "get":
                attr_dict = dict()

                product = await ProductLoader.get(item_id=kwargs['id']) # Получаем сам товар
                attributes = await AttrValuesLoader.get_all_attrs_of_product(product.id) # Получае значения атрибутов
                category_ids = await ProductCategoriesLoader.get_all_categories_of_product(product.id)
                categories = [await CategoryLoader.get(item_id=category_id) for category_id in category_ids]
                categories = [{"id": category.id, "name": category.name} for category in categories]

                for attr in attributes:
                    attribute = await AttributesLoader.get(item_id=attr["attribute_id"])
                    attr_dict[attribute.name] = attr.get("value")

                product_info = await product.to_dict()
                product_info["attributes"] = attr_dict
                product_info["category"] = categories

                return product_info
                
            case "post":
                # 1. Сначала проверяем наличие категории в таблице категорий
                category_name = kwargs['dto'].pop('category_name')
                category = await CategoryLoader.get_category_by_name(category_name=category_name)

                # 2. Если категория не найдена, возвращаем ошибку
                if category is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST, 
                        detail=f"Category \"{category_name}\" not found"
                    )

                # 3. Создаем продукт
                prod_opts = kwargs["dto"].pop("options")
                product = await ProductLoader.create(**kwargs['dto'])

                # 4. Если категория найдена, проверяем для каждого атрибута его наличие в таблице.
                # Если атрибут не найден, создаем его.
                options_of_category_ids = await CategoryAttrsLoader.get_all_attrs_of_category(category_id=category.id)
                options_of_category = [await AttributesLoader.get(item_id=attr_id) for attr_id in options_of_category_ids]
                options_of_category_names = [opt.name for opt in options_of_category]
                for option in prod_opts.keys():
                    if option not in options_of_category_names:
                        option = await AttributesLoader.create(name=option)
                        await CategoryAttrsLoader.create_relation(category_id=category.id, attribute_id=option.id)

                # 5. Присваиваем значения атрибутам продукта
                pr_attr_rels = []
                for option in options_of_category:
                    if option.name in prod_opts.keys():
                        pr_attr_rel = await AttrValuesLoader.create_value_of_attr(
                            attr_id=option.id, 
                            product_id=product.id, 
                            value=prod_opts[option.name]
                        )
                        pr_attr_rels.append(pr_attr_rel)

                # 6. Формируем json-ответ
                product_resp = await product.to_dict()
                product_resp["category"] = category.name
                product_resp["options"] = dict()

                attr_values = {rel["attribute_id"]: rel["value"] for rel in pr_attr_rels}
                for option in options_of_category:
                    if option.name in prod_opts.keys():
                        product_resp["options"][option.name] = attr_values[option.id]

                return product_resp
                
            case "patch":
                # 1. Проверяем, есть ли вообще такой товар в БД
                category_id = None
                update_attrs_results = []

                product = await ProductLoader.get(item_id=kwargs['id'])
                if not product:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Товар не найден"
                    )

                # 2. Если товар найден, и передана категория, проверяем наличие категории
                category = None
                if category_name := kwargs["dto"].get("category_name", None):
                    category = await CategoryLoader.get_category_by_name(category_name=category_name)
                    if not category:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail="Категория не найден"
                        )
                    category_id = category.id

                # 3. Изменяем (добавляем) категорию у товара
                categories_ids = await ProductCategoriesLoader.get_all_categories_of_product(product.id)
                categories_of_prod = [await CategoryLoader.get(item_id=category_id) for category_id in categories_ids]
                categories_of_prod = set([category.name for category in categories_of_prod])
                if category_name and category_name not in categories_of_prod:
                    # добавляем категорию к товару
                    await ProductCategoriesLoader.create_relation(product_id=product.id, category_id=category_id)
                    
                    
                # 4. Если переданы атрибуты, нам надо проверить наличие атрибутов, их значений,
                # обновить значения существующих атрибутов, а если каких-то атрибутов нет - 404
                attrs_of_product = list([])
                if options := kwargs["dto"].pop("options", None):
                    # 4.1. Получаем значения атрибутов товара
                    attrs_set = set(options.keys())
                    attrs_info = await AttrValuesLoader.get_all_attrs_of_product(product.id)
                    i = 0

                    # 4.2 Достаем атрибуты товара
                    for attr in attrs_info:
                        attribute = await AttributesLoader.get(item_id=attr["attribute_id"])
                        attrs_of_product.append(attribute)
                        
                    # 4.3. Проверяем, что атрибуты из DTO есть в атрибутах товара
                    attrs_of_product_set = set([attr.name for attr in attrs_of_product])
                    if attrs_set > attrs_of_product_set:
                        misssing_attrs = list(attrs_set - attrs_of_product_set)
                        raise HTTPException(
                            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=f"A few attributes don't exist for category of product: {misssing_attrs}"
                        )

                    # 4.4. Изменяем соответствующие атрибуты из DTO
                    attr_prod_map = {attr.name: attr.id for attr in attrs_of_product} # маппим атрибуты
                    options_ids = {option: attr_prod_map[option] for option in options.keys()}
                    for option, value in options.items():
                        update_attr_info = await AttrValuesLoader.update_value_of_attr(
                            attr_id = options_ids[option],
                            product_id = product.id,
                            new_value = value
                        )
                        update_attr_info.pop("product_id")
                        update_attrs_results.append(update_attr_info)
                        
                # 6. Обновляем оставшиеся характеристики товара
                product = await ProductLoader.update(item_id=kwargs["id"], **kwargs["dto"])

                # 7. Формируем ответ
                res_info = await product.to_dict()
                if category_id is not None:
                    res_info["category"] = {"category_id": category_id, "category_name": category.name}
                if options:
                    res_info["updated_options"] = update_attrs_results

                return res_info
                
            case "delete":
                item_dict = await ProductLoader.delete(item_id=kwargs['id'])
                return item_dict
                
    except ValueError as e:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except AttributeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        if isinstance(e, HTTPException) and e.status_code < 500:
            raise e

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )