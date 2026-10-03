from datetime import datetime

from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.notification import Notification


@celery_app.task
def test_background_task(name: str) -> str:
    return f"Background task completed for {name}."


@celery_app.task
def process_notification(notification_id: int) -> str:
    db = SessionLocal()

    try:
        notification = db.get(
            Notification,
            notification_id,
        )

        if not notification:
            return (
                f"Notification {notification_id} "
                "not found."
            )

        if notification.status == "READ":
            return (
                f"Notification {notification_id} "
                "is already READ."
            )

        notification.status = "SENT"
        notification.sent_at = datetime.utcnow()

        db.commit()

        return (
            f"Notification {notification_id} "
            "processed successfully."
        )

    finally:
        db.close()