from pydantic import BaseModel, Field

class ProductDto:
    
    class Create(BaseModel):
        name: str = Field(max_length=200)
        quantity: int = Field(ge=0)
        price: float = Field(gt=0)
        category_name: str = Field(max_length=100)
        options: dict[str, str] = Field(default_factory=dict) # Характеристики товара

        class Config:
            title = "ProductCreate"
        

    class Update(BaseModel):
        name: str | None = Field(default=None, max_length=200)
        quantity: int | None = Field(default=None, ge=0)
        price: float | None = Field(default=None, gt=0)
        category_name: str | None = Field(default=None, max_length=100)
        options: dict[str, str] | None = Field(default_factory=dict)
    
        class Config:
            title = "ProductUpdate"