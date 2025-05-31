from typing_extensions import Self

from pydantic import BaseModel, model_validator, constr, conint, confloat

class ProductDto:
    
    class Create(BaseModel):
        product_type: str
        name: constr(max_length=200)
        desctiption: constr(max_length=700) | None
        quantity: conint(ge=0)
        price: confloat(gt=0)

        @model_validator(mode='after')
        def validate_product_type(self) -> Self:

            allowed = {"Guitar", "Combo Amplifier", "Processor", "Effect Pedal"}
            if self.product_type not in allowed:
                raise ValueError(f'Product Type must be one of {allowed}')
            return self
        

    class Update(BaseModel):
        product_type: str | None
        name: constr(max_length=200) | None
        desctiption: constr(max_length=700) | None
        quantity: conint(ge=0) | None
        price: confloat(gt=0) | None

        @model_validator(mode='after')
        def validate_product_type(self) -> Self:

            allowed = {"Guitar", "Combo Amplifier", "Processor", "Effect Pedal"}
            if self.product_type not in allowed:
                raise ValueError(f'Product Type must be one of {allowed}')
            return self