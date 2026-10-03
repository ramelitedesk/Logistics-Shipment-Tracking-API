from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from app.core.order_status import OrderStatus

class OrderItemCreate(BaseModel):
    product_name: str = Field(
        min_length=2,
        max_length=200,
    )
    quantity: int = Field(
        gt=0,
    )
    unit_price: float = Field(
        ge=0,
    )


class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    product_name: str
    quantity: int
    unit_price: float
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class OrderCreate(BaseModel):
    customer_id: int
    order_number: str = Field(
        min_length=3,
        max_length=50,
    )
    notes: str | None = None
    items: list[OrderItemCreate] = Field(
        min_length=1,
    )


class OrderUpdate(BaseModel):
    status: OrderStatus | None = None
    notes: str | None = None


class OrderResponse(BaseModel):
    id: int
    customer_id: int
    order_number: str
    status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse]

    model_config = ConfigDict(
        from_attributes=True,
    )