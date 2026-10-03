from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WarehouseCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=150,
    )

    code: str = Field(
        min_length=2,
        max_length=50,
    )

    address_line1: str = Field(
        min_length=2,
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

    contact_phone: str | None = Field(
        default=None,
        max_length=30,
    )

    contact_email: str | None = Field(
        default=None,
        max_length=255,
    )

    is_active: bool = True

    description: str | None = None


class WarehouseUpdate(BaseModel):
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

    address_line1: str | None = Field(
        default=None,
        min_length=2,
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

    contact_phone: str | None = Field(
        default=None,
        max_length=30,
    )

    contact_email: str | None = Field(
        default=None,
        max_length=255,
    )

    is_active: bool | None = None

    description: str | None = None


class WarehouseResponse(BaseModel):
    id: int
    name: str
    code: str
    address_line1: str
    address_line2: str | None
    city: str
    state: str
    postal_code: str
    country: str
    contact_phone: str | None
    contact_email: str | None
    is_active: bool
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )