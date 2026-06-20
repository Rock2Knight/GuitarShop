from pydantic import BaseModel,Field

class OrderProductDto:

    class Create(BaseModel):
        order_id: int = Field(gt=0)
        product_id: int = Field(gt=0)
        quantity: int = Field(gt=0)

        class Config:
            title = "OrderProductCreate"


    class Update(BaseModel):
        order_id: int | None = Field(None, gt=0)
        product_id: int | None = Field(None, gt=0)
        quantity: int | None = Field(None, gt=0)
        
        class Config:
            title = "OrderProductUpdate"