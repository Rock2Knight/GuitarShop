from typing_extensions import Self

from pydantic import model_validator, constr, conint, confloat

from app.dto.product import ProductDto

class EffectPedalDto(ProductDto):

    class Create(ProductDto.Create):
        effect: str

        class Config:
            title = "EffectPedalCreate"

    class Update(ProductDto.Update):
        effect: str | None = None

        class Config:
            title = "EffectPedalUpdate"