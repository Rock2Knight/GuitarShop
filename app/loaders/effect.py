from app.models import EffectPedal
from app.loaders.model_loader import ModelLoader

class EffectLoader(ModelLoader[EffectPedal]):
    model = EffectPedal