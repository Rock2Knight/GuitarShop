from typing_extensions import Self

from pydantic import model_validator, constr, conint, confloat

from dto.product import ProductDto

class EffectPedalDto(ProductDto):

    class Create(ProductDto.Create):
        effect: str

    class Update(ProductDto.Update):
        effect: str | None