from models import CartProduct
from loaders.model_loader import ModelLoader

class CartProductLoader(ModelLoader):
    model: CartProduct = CartProduct