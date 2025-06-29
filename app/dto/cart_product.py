from typing_extensions import Self

from pydantic import BaseModel, model_validator, conint

class CartProductDto:

    class Create(BaseModel):
        cart_id: conint(gt=0)
        guitar_id: conint(gt=0) | None
        combo_id: conint(gt=0) | None
        processor_id: conint(gt=0) | None
        effect_id: conint(gt=0) | None
        quantity: conint(gt=0)

        @model_validator(mode='after')
        def validate_single_product(self) -> Self:
            provided_ids = sum(1 for field in [
                self.guitar_id, 
                self.combo_id, 
                self.processor_id, 
                self.effect_id
            ] if field is not None)
            
            if provided_ids != 1:
                raise ValueError('Должен быть указан ровно один ID товара (гитара, комбо, процессор или эффект)')
            return self


    class Update(BaseModel):
        cart_id: conint(gt=0)
        guitar_id: conint(gt=0) | None
        combo_id: conint(gt=0) | None
        processor_id: conint(gt=0) | None
        effect_id: conint(gt=0) | None
        quantity: conint(gt=0)

        @model_validator(mode='after')
        def validate_single_product(self) -> Self:
            provided_ids = sum(1 for field in [
                self.guitar_id, 
                self.combo_id, 
                self.processor_id, 
                self.effect_id
            ] if field is not None)
            
            if provided_ids != 1:
                raise ValueError('Должен быть указан ровно один ID товара (гитара, комбо, процессор или эффект)')
            return self