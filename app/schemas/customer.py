from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CustomerCreate(BaseModel):
    user_id: int
    phone: str | None = Field(
        default=None,
        max_length=30,
    )
    company_name: str | None = Field(
        default=None,
        max_length=150,
    )


class CustomerUpdate(BaseModel):
    phone: str | None = Field(
        default=None,
        max_length=30,
    )
    company_name: str | None = Field(
        default=None,
        max_length=150,
    )


class CustomerResponse(BaseModel):
    id: int
    user_id: int
    phone: str | None
    company_name: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )