from app.workers.tasks import process_notification


def dispatch_notification(notification_id: int):
    return process_notification.delay(
        notification_id
    )