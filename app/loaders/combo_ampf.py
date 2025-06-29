from app.models import ComboAmplifier 
from app.loaders.model_loader import ModelLoader

class ComboAmpfLoader(ModelLoader[ComboAmplifier]):
    model = ComboAmplifier