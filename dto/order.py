from typing_extensions import Self

from pydantic import BaseModel, model_validator, constr

from models import OrderStatus

class OrderDto(BaseModel):
    status: OrderStatus | None
    order_date: constr(pattern=r'^[0-9]{4}-[0-9]{2}-[0-9]{2}$') | None