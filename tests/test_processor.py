"""This module contains tests for guitar processors."""
from app.models import Processor
from tests.base_test_product import BaseTestProduct


class TestProcessor(BaseTestProduct):
    
    product = Processor
    endpoint_prefix = "/processor"
    test_data = {
        "FIRST_EXPECTED": {
            "description": None,
            "product_type": "Processor",
            "name": "Valeton GP-100",
            "quantity": 40,
            "price": 14800,
            "express_pedal": True,
            "instrument_type": "гитара",
            "screen_type": "цветной"
        },
        "TEST_BODY": {
            "product_type": "Processor",
            "name": "BOSS RC-500",
            "quantity": 34,
            "price": 33490,
            "express_pedal": True,
            "instrument_type": "универсальный",
            "screen_type": "универсальный"
        },
        "TEST_UPDATED_DATA": {
            "description": "Этот процессор - точно ваш выбор!",
            "price": 25000
        }    
    }
