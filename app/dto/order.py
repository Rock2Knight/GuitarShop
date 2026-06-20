from datetime import datetime
from typing_extensions import Self

from pydantic import BaseModel, model_validator, Field

from app.models import OrderStatus

class OrderDto(BaseModel):
    status: OrderStatus = "New"
    order_date: str = Field(default=datetime.now().strftime("%Y-%m-%d"), pattern=r'^[0-9]{4}-[0-9]{2}-[0-9]{2}$')

    @model_validator(mode='after')
    def validate_product_type(self) -> Self:
        allowed_statuses = ["New", "In Progress", "Completed", "Canceled"]
        if self.status and self.status not in allowed_statuses:
            raise ValueError("Указан неавлидный статус заказа")
        
        if not self.status and not self.order_date:
            raise ValueError("Не указано не одно поле в запросе!")
        
        return self
    
    class Config:
        title = "OrderCreate"