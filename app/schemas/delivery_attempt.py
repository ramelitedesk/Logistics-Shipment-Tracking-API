from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class DeliveryAttemptStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    RESCHEDULED = "RESCHEDULED"


class DeliveryAttemptCreate(BaseModel):
    shipment_id: int
    delivery_agent_id: int
    status: DeliveryAttemptStatus
    failure_reason: str | None = Field(
        default=None,
        max_length=255,
    )
    notes: str | None = None


class DeliveryAttemptUpdate(BaseModel):
    status: DeliveryAttemptStatus | None = None
    failure_reason: str | None = Field(
        default=None,
        max_length=255,
    )
    notes: str | None = None


class DeliveryAttemptResponse(BaseModel):
    id: int
    shipment_id: int
    delivery_agent_id: int
    attempt_number: int
    attempted_at: datetime
    status: str
    failure_reason: str | None
    notes: str | None

    model_config = ConfigDict(
        from_attributes=True,
    )