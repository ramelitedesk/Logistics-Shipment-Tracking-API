from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ShipmentAssignmentCreate(BaseModel):
    shipment_id: int
    delivery_agent_id: int


class ShipmentAssignmentUpdate(BaseModel):
    delivery_agent_id: int
    is_active: bool | None = None


class ShipmentAssignmentResponse(BaseModel):
    id: int
    shipment_id: int
    delivery_agent_id: int
    assigned_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)