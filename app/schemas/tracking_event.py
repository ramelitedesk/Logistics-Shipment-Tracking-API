from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.shipment_status import ShipmentStatus


class TrackingEventCreate(BaseModel):
    shipment_id: int

    status: ShipmentStatus

    location: str | None = Field(
        default=None,
        max_length=255,
    )

    facility: str | None = Field(
        default=None,
        max_length=255,
    )

    description: str | None = None

    event_time: datetime | None = None

    source: str = Field(
        default="SYSTEM",
        min_length=3,
        max_length=50,
    )


class TrackingEventResponse(BaseModel):
    id: int
    shipment_id: int
    status: ShipmentStatus
    location: str | None
    facility: str | None
    description: str | None
    event_time: datetime
    created_by: int | None
    source: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )