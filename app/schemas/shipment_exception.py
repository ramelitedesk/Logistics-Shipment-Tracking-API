from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ShipmentExceptionType(str, Enum):
    DAMAGED = "DAMAGED"
    LOST = "LOST"
    ADDRESS_ISSUE = "ADDRESS_ISSUE"
    CUSTOMER_UNAVAILABLE = "CUSTOMER_UNAVAILABLE"
    WEATHER_DELAY = "WEATHER_DELAY"
    OTHER = "OTHER"


class ShipmentExceptionStatus(str, Enum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"


class ShipmentExceptionCreate(BaseModel):
    shipment_id: int

    exception_type: ShipmentExceptionType

    description: str = Field(
        min_length=3,
    )

    status: ShipmentExceptionStatus = (
        ShipmentExceptionStatus.OPEN
    )

    resolution_notes: str | None = None


class ShipmentExceptionUpdate(BaseModel):
    exception_type: ShipmentExceptionType | None = None

    description: str | None = Field(
        default=None,
        min_length=3,
    )

    status: ShipmentExceptionStatus | None = None

    resolution_notes: str | None = None


class ShipmentExceptionResponse(BaseModel):
    id: int
    shipment_id: int
    exception_type: str
    description: str
    reported_by: int | None
    status: str
    resolved_at: datetime | None
    resolution_notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )