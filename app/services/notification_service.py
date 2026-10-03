from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.shipment import Shipment
from app.models.user import User
from app.schemas.notification import (
    NotificationCreate,
    NotificationUpdate,
)


def create_notification(
    db: Session,
    notification_data: NotificationCreate,
) -> Notification:

    user = db.get(User, notification_data.user_id)

    if not user:
        raise ValueError("Notification user not found.")

    if notification_data.shipment_id is not None:
        shipment = db.get(
            Shipment,
            notification_data.shipment_id,
        )

        if not shipment:
            raise ValueError("Notification shipment not found.")

    notification = Notification(
        user_id=notification_data.user_id,
        shipment_id=notification_data.shipment_id,
        notification_type=notification_data.notification_type.value,
        channel=notification_data.channel.value,
        title=notification_data.title,
        message=notification_data.message,
        status=notification_data.status.value,
    )

    if notification.status == "SENT":
        notification.sent_at = datetime.utcnow()

    if notification.status == "READ":
        notification.sent_at = datetime.utcnow()
        notification.read_at = datetime.utcnow()

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification


def get_notification(
    db: Session,
    notification_id: int,
) -> Notification | None:

    return db.get(
        Notification,
        notification_id,
    )


def get_notifications(
    db: Session,
) -> list[Notification]:

    return list(
        db.scalars(
            select(Notification)
            .order_by(Notification.id.desc())
        ).all()
    )


def get_notifications_by_user(
    db: Session,
    user_id: int,
) -> list[Notification]:

    return list(
        db.scalars(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.id.desc())
        ).all()
    )


def get_notifications_by_shipment(
    db: Session,
    shipment_id: int,
) -> list[Notification]:

    return list(
        db.scalars(
            select(Notification)
            .where(Notification.shipment_id == shipment_id)
            .order_by(Notification.id.desc())
        ).all()
    )


def update_notification(
    db: Session,
    notification_id: int,
    notification_data: NotificationUpdate,
) -> Notification | None:

    notification = db.get(
        Notification,
        notification_id,
    )

    if not notification:
        return None

    if notification_data.status is not None:

        new_status = notification_data.status.value

        if new_status == "SENT":
            notification.status = "SENT"

            if notification.sent_at is None:
                notification.sent_at = datetime.utcnow()

        elif new_status == "READ":
            notification.status = "READ"

            if notification.sent_at is None:
                notification.sent_at = datetime.utcnow()

            if notification.read_at is None:
                notification.read_at = datetime.utcnow()

        elif new_status == "PENDING":
            notification.status = "PENDING"
            notification.read_at = None

        elif new_status == "FAILED":
            notification.status = "FAILED"

    db.commit()
    db.refresh(notification)

    return notification


def mark_notification_as_read(
    db: Session,
    notification_id: int,
) -> Notification | None:

    notification = db.get(
        Notification,
        notification_id,
    )

    if not notification:
        return None

    notification.status = "READ"

    if notification.sent_at is None:
        notification.sent_at = datetime.utcnow()

    notification.read_at = datetime.utcnow()

    db.commit()
    db.refresh(notification)

    return notification