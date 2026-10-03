from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class WebhookStatus(str, Enum):
    RECEIVED = "RECEIVED"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"


class WebhookCreate(BaseModel):
    carrier_id: int | None = None
    shipment_id: int | None = None
    event_type: str = Field(min_length=2, max_length=100)
    external_event_id: str | None = Field(
        default=None,
        max_length=255,
    )
    payload: str = Field(min_length=2)
    signature: str | None = Field(
        default=None,
        max_length=500,
    )


class WebhookUpdate(BaseModel):
    status: WebhookStatus | None = None
    error_message: str | None = None


class WebhookResponse(BaseModel):
    id: int
    carrier_id: int | None
    shipment_id: int | None
    event_type: str
    external_event_id: str | None
    payload: str
    signature: str | None
    status: str
    processed_at: datetime | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)