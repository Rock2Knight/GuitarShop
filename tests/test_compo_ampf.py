"""This module contains tests for combo amplifiers."""
from models import ComboAmplifier
from tests.base_test_product import BaseTestProduct


class TestComboAmplifier(BaseTestProduct):
    
    product = ComboAmplifier
    endpoint_prefix = "/combo_ampf"
    test_data = {
        "FIRST_EXPECTED": {
            "description": None,
            "product_type": "Combo Amplifier",
            "name": "IBANEZ IBZ10GV2",
            "quantity": 30,
            "price": 27000,
            "power": 15,
            "channels_count": 2,
            "combo_type": "Transistor",
            "effects": "есть"
        },
        "TEST_BODY": {
            "product_type": "Combo Amplifier",
            "name": "BOSS KTN-50 Gen3",
            "quantity": 22,
            "price": 34390,
            "power": 50,
            "channels_count": 2,
            "combo_type": "Transistor",
            "effects": "есть"
        },
        "TEST_UPDATED_DATA": {
            "description": "Этот комбо-усилитель - точно для вас!",
            "price": 30000
        }    
    }
