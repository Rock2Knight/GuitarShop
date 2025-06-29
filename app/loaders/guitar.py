from app.models import Guitar
from app.loaders.model_loader import ModelLoader

class GuitarLoader(ModelLoader[Guitar]):
    model = Guitar