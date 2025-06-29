from models import EffectPedal
from loaders.model_loader import ModelLoader

class EffectLoader(ModelLoader[EffectPedal]):
    model = EffectPedal