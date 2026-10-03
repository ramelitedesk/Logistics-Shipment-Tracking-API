from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProofOfDeliveryCreate(BaseModel):
    shipment_id: int
    delivery_attempt_id: int

    recipient_name: str = Field(
        min_length=2,
        max_length=150,
    )

    signature_reference: str | None = Field(
        default=None,
        max_length=500,
    )

    photo_reference: str | None = Field(
        default=None,
        max_length=500,
    )

    notes: str | None = None


class ProofOfDeliveryUpdate(BaseModel):
    recipient_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    signature_reference: str | None = Field(
        default=None,
        max_length=500,
    )

    photo_reference: str | None = Field(
        default=None,
        max_length=500,
    )

    notes: str | None = None


class ProofOfDeliveryResponse(BaseModel):
    id: int
    shipment_id: int
    delivery_attempt_id: int
    recipient_name: str
    signature_reference: str | None
    photo_reference: str | None
    delivered_at: datetime
    notes: str | None

    model_config = ConfigDict(
        from_attributes=True,
    )