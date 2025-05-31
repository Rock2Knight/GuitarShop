from database import connection
from models import Cart
from loaders.model_loader import ModelLoader

class CartLoader(ModelLoader):
    model: Cart = Cart