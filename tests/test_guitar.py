"""This module contains tests for guitars."""
from models import Guitar
from tests.base_test_product import BaseTestProduct


class TestGuitar(BaseTestProduct):
    product = Guitar
    endpoint_prefix = "/guitar"
    test_data = {
        "FIRST_EXPECTED": {
            "guitar_type": "Electric",
            "shape": "SuperStrat",
            "fret_count": 22,
            "description": None,
            "recorder_config": "s-s-h",
            "fingerboard_material": "клен",
            "body_material": "тополь",
            "product_type": "Guitar",
            "name": "IBANEZ GRX40-BKN",
            "quantity": 30,
            "price": 27000
        },
        "TEST_BODY": {
            "product_type": "Guitar",
            "name": "ROCKDALE Stars TE HH Black",
            "quantity": 22,
            "price": 11100,
            "guitar_type": "Electric",
            "shape": "Telecaster",
            "fret_count": 22,
            "recorder_config": "h-h",
            "fingerboard_material": "клен",
            "body_material": "тополь"
        },
        "TEST_UPDATED_DATA": {
            "description": "Это очень крутая гитара для тяжелой музыки! Это точно ваш выбор!",
            "price": 22000
        }    
    }
