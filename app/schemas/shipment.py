from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.shipment_status import ShipmentStatus


class ShipmentCreate(BaseModel):
    order_id: int

    shipment_number: str = Field(
        min_length=3,
        max_length=50,
    )

    tracking_number: str | None = Field(
        default=None,
        max_length=100,
    )

    origin_warehouse_id: int | None = None

    destination_warehouse_id: int | None = None


class ShipmentUpdate(BaseModel):
    status: ShipmentStatus | None = None

    tracking_number: str | None = Field(
        default=None,
        max_length=100,
    )

    origin_warehouse_id: int | None = None

    destination_warehouse_id: int | None = None


class ShipmentResponse(BaseModel):
    id: int
    order_id: int
    shipment_number: str
    status: str
    tracking_number: str | None

    origin_warehouse_id: int | None
    destination_warehouse_id: int | None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )