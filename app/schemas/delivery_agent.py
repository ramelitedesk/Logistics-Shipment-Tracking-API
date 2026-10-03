from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DeliveryAgentCreate(BaseModel):
    user_id: int
    employee_code: str = Field(min_length=2, max_length=50)
    phone: str = Field(min_length=5, max_length=30)
    vehicle_type: str | None = Field(default=None, max_length=50)
    vehicle_number: str | None = Field(default=None, max_length=50)
    license_number: str | None = Field(default=None, max_length=100)
    is_available: bool = True
    is_active: bool = True
    notes: str | None = None


class DeliveryAgentUpdate(BaseModel):
    phone: str | None = Field(default=None, min_length=5, max_length=30)
    vehicle_type: str | None = Field(default=None, max_length=50)
    vehicle_number: str | None = Field(default=None, max_length=50)
    license_number: str | None = Field(default=None, max_length=100)
    is_available: bool | None = None
    is_active: bool | None = None
    notes: str | None = None


class DeliveryAgentResponse(BaseModel):
    id: int
    user_id: int
    employee_code: str
    phone: str
    vehicle_type: str | None
    vehicle_number: str | None
    license_number: str | None
    is_available: bool
    is_active: bool
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)