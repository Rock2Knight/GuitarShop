#from sqlalchemy import select, delete, update
#from sqlalchemy.ext.asyncio import AsyncSession

#from database import connection
from loaders.model_loader import ModelLoader

from models import Processor

class ProcessorLoader(ModelLoader):
    model: Processor = Processor