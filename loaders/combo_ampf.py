from models import ComboAmplifier 
from loaders.model_loader import ModelLoader

class ComboAmpfLoader(ModelLoader[ComboAmplifier]):
    model = ComboAmplifier