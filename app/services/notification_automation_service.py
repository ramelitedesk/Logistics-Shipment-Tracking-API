from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.services.notification_dispatch_service import (
    dispatch_notification,
)


def create_and_dispatch_shipment_notification(
    db: Session,
    shipment_id: int,
    user_id: int,
    status: str,
    message: str,
):
    notification = Notification(
        user_id=user_id,
        shipment_id=shipment_id,
        notification_type="SHIPMENT_STATUS",
        channel="EMAIL",
        title=f"Shipment {status}",
        message=message,
        status="PENDING",
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    dispatch_notification(notification.id)

    return notification