from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class NotificationType(str, Enum):
    SHIPMENT_CREATED = "SHIPMENT_CREATED"
    SHIPMENT_STATUS_UPDATED = "SHIPMENT_STATUS_UPDATED"
    DELIVERY_ATTEMPT = "DELIVERY_ATTEMPT"
    DELIVERY_COMPLETED = "DELIVERY_COMPLETED"
    DELIVERY_FAILED = "DELIVERY_FAILED"
    EXCEPTION_CREATED = "EXCEPTION_CREATED"
    EXCEPTION_RESOLVED = "EXCEPTION_RESOLVED"
    GENERAL = "GENERAL"


class NotificationChannel(str, Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    PUSH = "PUSH"
    IN_APP = "IN_APP"


class NotificationStatus(str, Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"
    READ = "READ"


class NotificationCreate(BaseModel):
    user_id: int
    shipment_id: int | None = None
    notification_type: NotificationType
    channel: NotificationChannel = NotificationChannel.IN_APP
    title: str = Field(min_length=2, max_length=255)
    message: str = Field(min_length=2)
    status: NotificationStatus = NotificationStatus.PENDING


class NotificationUpdate(BaseModel):
    status: NotificationStatus | None = None


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    shipment_id: int | None
    notification_type: str
    channel: str
    title: str
    message: str
    status: str
    sent_at: datetime | None
    read_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)