from pydantic import BaseModel,Field

from app.models import OrderStatus

class OrderProductDto:

    class Create(BaseModel):
        status: OrderStatus = "New"
        order_id: int = Field(gt=0)
        cart_product_id: int = Field(gt=0)

        class Config:
            title = "OrderProductCreate"


    class Update(BaseModel):
        status: OrderStatus | None = Field(None, description="Статус заказа")
        order_id: int | None = Field(None, gt=0)
        cart_product_id: int | None = Field(None, gt=0)
        
        class Config:
            title = "OrderProductUpdate"