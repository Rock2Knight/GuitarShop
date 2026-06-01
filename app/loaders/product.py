from app.models import Product
from app.loaders.model_loader import ModelLoader

class ProductLoader(ModelLoader[Product]):
    model = Product