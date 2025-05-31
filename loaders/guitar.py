#from sqlalchemy import select, delete, update
#from sqlalchemy.ext.asyncio import AsyncSession

#from database import connection
from models import Guitar

from loaders.model_loader import ModelLoader

class GuitarLoader(ModelLoader):
    model: Guitar = Guitar