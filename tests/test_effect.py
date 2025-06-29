"""This module contains tests for effect pedals."""
from app.models import EffectPedal
from tests.base_test_product import BaseTestProduct


class TestEffectPedal(BaseTestProduct):
    
    product = EffectPedal
    endpoint_prefix = "/effect"
    test_data = {
        "FIRST_EXPECTED": {
            "description": None,
            "product_type": "Effect Pedal",
            "name": "BOSS DS-1",
            "quantity": 40,
            "price": 9900,
            "effect": "distortion"
        },
        "TEST_BODY": {
            "product_type": "Effect Pedal",
            "name": "Nux Cherub NOD-2 Tube Man Overdrive",
            "quantity": 50,
            "price": 3970,
            "effect": "overdrive"
        },
        "TEST_UPDATED_DATA": {
            "description": "Вам точно нужна данная педаль эффектов!",
            "price": 3500
        }    
    }
