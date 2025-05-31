from typing_extensions import Self

from pydantic import model_validator, constr, conint, confloat

from dto.product import ProductDto

class GuitarDto:
    
    class Create(ProductDto.Create):
        guitar_type: constr(max_length=20)
        shape: constr(max_length=30)
        fret_count: conint(le=25)
        recorder_config: constr(max_length=10) | None
        fingerboard_material: str
        body_material: str

        @model_validator(mode='after')
        def validate_guitar(self) -> Self:

            gtype_allowed = {"Acoustic", "Electric", }
            if self.guitar_type not in gtype_allowed:
                raise ValueError(f'Product Type must be one of {gtype_allowed}')

            shape_allowed = {"Classic", "Les Paul", "Stratocaster",
                            "Telecaster", "SuperStrat", "Explorer",
                            "SG", "PRS", "Flying V", "Mocking Bird",
                            "Warlock", "RR", "Star", "Ice Man", 
                            "FireBird", "Jaguar", "Mustang", "Jag-Stang"}
            if self.shape not in shape_allowed:
                raise ValueError(f'Shape must be one of {shape_allowed}')

            configs = {'s-s', 's-s-s', 'h-h', 's-s-h', 'h-s',
                       'h-s-h', 'j-j', 'split-p', 'p-j'}

            if self.recorder_config is not None:
                if self.recorder_config not in configs:
                    raise ValueError(f'Recorder Config must be one of {configs}')

            return self
        

    class Update(ProductDto.Update):
        guitar_type: constr(max_length=20) | None
        shape: constr(max_length=30) | None
        fret_count: conint(le=25) | None
        recorder_config: constr(max_length=10) | None
        fingerboard_material: str | None
        body_material: str | None

        @model_validator(mode='after')
        def validate_guitar(self) -> Self:

            gtype_allowed = {"Acoustic", "Electric", }
            if self.guitar_type not in gtype_allowed:
                raise ValueError(f'Product Type must be one of {gtype_allowed}')

            shape_allowed = {"Classic", "Les Paul", "Stratocaster",
                            "Telecaster", "SuperStrat", "Explorer",
                            "SG", "PRS", "Flying V", "Mocking Bird",
                            "Warlock", "RR", "Star", "Ice Man", 
                            "FireBird", "Jaguar", "Mustang", "Jag-Stang"}
            if self.shape not in shape_allowed:
                raise ValueError(f'Shape must be one of {shape_allowed}')

            configs = {'s-s', 's-s-s', 'h-h', 's-s-h', 'h-s',
                       'h-s-h', 'j-j', 'split-p', 'p-j'}

            if self.recorder_config is not None:
                if self.recorder_config not in configs:
                    raise ValueError(f'Recorder Config must be one of {configs}')

            return self