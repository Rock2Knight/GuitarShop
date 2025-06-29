from app.models import CartProduct
from app.loaders.model_loader import ModelLoader

class CartProductLoader(ModelLoader[CartProduct]):
    model: CartProduct = CartProduct