from app.database import connection
from app.models import Cart
from app.loaders.model_loader import ModelLoader

class CartLoader(ModelLoader[Cart]):
    model: Cart = Cart