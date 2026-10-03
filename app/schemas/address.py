from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AddressCreate(BaseModel):
    customer_id: int
    address_type: str = Field(
        default="SHIPPING",
        min_length=3,
        max_length=30,
    )
    address_line1: str = Field(
        min_length=3,
        max_length=255,
    )
    address_line2: str | None = Field(
        default=None,
        max_length=255,
    )
    city: str = Field(
        min_length=2,
        max_length=100,
    )
    state: str = Field(
        min_length=2,
        max_length=100,
    )
    postal_code: str = Field(
        min_length=3,
        max_length=20,
    )
    country: str = Field(
        default="India",
        min_length=2,
        max_length=100,
    )
    is_default: bool = False


class AddressUpdate(BaseModel):
    address_type: str | None = Field(
        default=None,
        min_length=3,
        max_length=30,
    )
    address_line1: str | None = Field(
        default=None,
        min_length=3,
        max_length=255,
    )
    address_line2: str | None = Field(
        default=None,
        max_length=255,
    )
    city: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )
    state: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )
    postal_code: str | None = Field(
        default=None,
        min_length=3,
        max_length=20,
    )
    country: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )
    is_default: bool | None = None


class AddressResponse(BaseModel):
    id: int
    customer_id: int
    address_type: str
    address_line1: str
    address_line2: str | None
    city: str
    state: str
    postal_code: str
    country: str
    is_default: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )