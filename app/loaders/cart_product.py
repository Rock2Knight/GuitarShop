from typing import override

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import connection
from app.models import CartProduct
from app.loaders.model_loader import ModelLoader

class CartProductLoader(ModelLoader[CartProduct]):
    model: CartProduct = CartProduct