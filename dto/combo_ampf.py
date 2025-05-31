from typing_extensions import Self

from pydantic import model_validator, constr, conint, confloat

from dto.product import ProductDto

class ComboAmpfDto(ProductDto):

    class Create(ProductDto.Create):
        combo_type: constr(min_length=1)
        effects: str
        channels_count: conint(gt=0)
        power: confloat(gt=0)

        @model_validator(mode="after")
        def validate_combo_ampf(self) -> Self:
            pass


    class Update(ProductDto.Update):
        combo_type: constr(min_length=1) | None
        effects: str | None
        channels_count: conint(gt=0) | None
        power: confloat(gt=0) | None

        @model_validator(mode="after")
        def validate_combo_ampf(self) -> Self:
            pass