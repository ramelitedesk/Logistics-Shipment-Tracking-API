from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CarrierCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=150,
    )

    code: str = Field(
        min_length=2,
        max_length=50,
    )

    contact_email: str | None = None

    contact_phone: str | None = Field(
        default=None,
        max_length=30,
    )

    api_base_url: str | None = Field(
        default=None,
        max_length=500,
    )

    is_active: bool = True

    description: str | None = None


class CarrierUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    code: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
    )

    contact_email: str | None = None

    contact_phone: str | None = Field(
        default=None,
        max_length=30,
    )

    api_base_url: str | None = Field(
        default=None,
        max_length=500,
    )

    is_active: bool | None = None

    description: str | None = None


class CarrierResponse(BaseModel):
    id: int
    name: str
    code: str
    contact_email: str | None
    contact_phone: str | None
    api_base_url: str | None
    is_active: bool
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )