from typing_extensions import Self

from pydantic import model_validator, constr, conint, confloat

from app.dto.product import ProductDto

class ComboAmpfDto(ProductDto):

    class Create(ProductDto.Create):
        combo_type: constr(min_length=1)
        effects: str
        channels_count: conint(gt=0)
        power: confloat(gt=0)

        @model_validator(mode="after")
        def validate_combo_ampf(self) -> Self:
            if not isinstance(self.effects, str):
                raise ValueError("В эффектах должна быть прописана строка!")
            if self.effects.lower() not in {"есть", "нет"}:
                raise ValueError("Невалидные значения эффектов")
            
            return self


    class Update(ProductDto.Update):
        combo_type: constr(min_length=1) | None = None
        effects: str | None = None
        channels_count: conint(gt=0) | None = None
        power: confloat(gt=0) | None = None

        @model_validator(mode="after")
        def validate_combo_ampf(self) -> Self:
            if self.effects is not None:
                if not isinstance(self.effects, str):
                    raise ValueError("В эффектах должна быть прописана строка!")
                if self.effects.lower() not in {"есть", "нет"}:
                    raise ValueError("Невалидные значения эффектов")
                
            return self