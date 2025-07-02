from typing_extensions import Self

from pydantic import BaseModel, model_validator, constr

from app.models import OrderStatus

class OrderDto(BaseModel):
    status: OrderStatus | None = None
    order_date: constr(pattern=r'^[0-9]{4}-[0-9]{2}-[0-9]{2}$') | None = None

    @model_validator(mode='after')
    def validate_product_type(self) -> Self:
        allowed_statuses = ["New", "In Progress", "Completed", "Canceled"]
        if self.status and self.status not in allowed_statuses:
            raise ValueError("Указан неавлидный статус заказа")
        
        if not self.status and not self.order_date:
            raise ValueError("Не указано не одно поле в запросе!")
        
        return self