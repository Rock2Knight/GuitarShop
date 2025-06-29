from app.loaders.model_loader import ModelLoader
from app.models import Processor

class ProcessorLoader(ModelLoader[Processor]):
    model = Processor