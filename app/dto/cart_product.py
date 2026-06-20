from pydantic import BaseModel, Field

class CartProductDto:

    class Create(BaseModel):
        cart_id: int = Field(gt=0)
        product_id: int = Field(gt=0)
        quantity: int = Field(gt=0)

        class Config:
            title = "CartProductCreate"

    class Update(BaseModel):
        cart_id: int | None = Field(default=None, gt=0)
        product_id: int | None = Field(default=None, gt=0)
        quantity: int | None = Field(default=None, gt=0)

        class Config:
            title = "CartProductUpdate"