from typing_extensions import Self

from pydantic import model_validator, constr, conint, confloat

from dto.product import ProductDto

class ProcessorDto(ProductDto):

    class Create(ProductDto.Create):
        express_pedal: bool = False
        instrument_type: str
        screen_type: str

    class Update(ProductDto.Update):
        express_pedal: bool | None = None
        instrument_type: str | None = None
        screen_type: str | None = None