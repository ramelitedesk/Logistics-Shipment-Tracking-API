import json
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.carrier import Carrier
from app.models.shipment import Shipment
from app.models.tracking_event import TrackingEvent
from app.models.webhook import Webhook
from app.schemas.shipment import ShipmentStatus
from app.schemas.webhook import WebhookCreate, WebhookUpdate
from app.services.notification_automation_service import (
    create_and_dispatch_shipment_notification,
)


def create_webhook(
    db: Session,
    webhook_data: WebhookCreate,
    created_by: int | None = None,
) -> Webhook:
    if webhook_data.carrier_id is not None:
        carrier = db.get(
            Carrier,
            webhook_data.carrier_id,
        )

        if not carrier:
            raise ValueError("Webhook carrier not found.")

    if webhook_data.shipment_id is not None:
        shipment = db.get(
            Shipment,
            webhook_data.shipment_id,
        )

        if not shipment:
            raise ValueError("Webhook shipment not found.")

    # Prevent duplicate external webhook events.
    if webhook_data.external_event_id:
        existing = db.scalar(
            select(Webhook).where(
                Webhook.external_event_id
                == webhook_data.external_event_id
            )
        )

        if existing:
            raise ValueError(
                "Webhook with this external event ID already exists."
            )

    # Validate that payload contains valid JSON.
    try:
        json.loads(webhook_data.payload)
    except json.JSONDecodeError:
        raise ValueError(
            "Webhook payload must contain valid JSON."
        )

    webhook = Webhook(
        carrier_id=webhook_data.carrier_id,
        shipment_id=webhook_data.shipment_id,
        event_type=webhook_data.event_type,
        external_event_id=webhook_data.external_event_id,
        payload=webhook_data.payload,
        signature=webhook_data.signature,
        status="RECEIVED",
    )

    db.add(webhook)

    # Generate webhook ID before creating audit log.
    db.flush()

    # Automatic audit log for webhook reception.
    audit_log = AuditLog(
        user_id=created_by,
        action="CREATE",
        entity_type="WEBHOOK",
        entity_id=webhook.id,
        old_value=None,
        new_value=json.dumps(
            {
                "carrier_id": webhook.carrier_id,
                "shipment_id": webhook.shipment_id,
                "event_type": webhook.event_type,
                "external_event_id": webhook.external_event_id,
                "status": webhook.status,
            }
        ),
    )

    try:
        db.add(audit_log)

        db.commit()
        db.refresh(webhook)

    except Exception:
        db.rollback()
        raise

    return webhook


def get_webhook(
    db: Session,
    webhook_id: int,
) -> Webhook | None:
    return db.get(
        Webhook,
        webhook_id,
    )


def get_webhooks(
    db: Session,
) -> list[Webhook]:
    return list(
        db.scalars(
            select(Webhook).order_by(
                Webhook.id.desc()
            )
        ).all()
    )


def get_webhooks_by_shipment(
    db: Session,
    shipment_id: int,
) -> list[Webhook]:
    return list(
        db.scalars(
            select(Webhook)
            .where(
                Webhook.shipment_id == shipment_id
            )
            .order_by(
                Webhook.id.desc()
            )
        ).all()
    )


def get_webhooks_by_carrier(
    db: Session,
    carrier_id: int,
) -> list[Webhook]:
    return list(
        db.scalars(
            select(Webhook)
            .where(
                Webhook.carrier_id == carrier_id
            )
            .order_by(
                Webhook.id.desc()
            )
        ).all()
    )


def update_webhook(
    db: Session,
    webhook_id: int,
    webhook_data: WebhookUpdate,
    updated_by: int | None = None,
) -> Webhook | None:
    webhook = db.get(
        Webhook,
        webhook_id,
    )

    if not webhook:
        return None

    # Capture old values.
    old_values = {
        "status": webhook.status,
        "error_message": webhook.error_message,
        "processed_at": (
            webhook.processed_at.isoformat()
            if webhook.processed_at
            else None
        ),
    }

    if webhook_data.error_message is not None:
        webhook.error_message = webhook_data.error_message

    if webhook_data.status is not None:
        new_status = webhook_data.status.value

        if new_status == "PROCESSED":
            webhook.status = "PROCESSED"
            webhook.processed_at = datetime.utcnow()
            webhook.error_message = None

        elif new_status == "FAILED":
            webhook.status = "FAILED"

            if webhook_data.error_message:
                webhook.error_message = (
                    webhook_data.error_message
                )

        elif new_status == "RECEIVED":
            webhook.status = "RECEIVED"
            webhook.processed_at = None

    # Capture new values.
    new_values = {
        "status": webhook.status,
        "error_message": webhook.error_message,
        "processed_at": (
            webhook.processed_at.isoformat()
            if webhook.processed_at
            else None
        ),
    }

    # Create audit log only if something changed.
    if old_values != new_values:
        audit_action = (
            "PROCESS"
            if (
                old_values["status"] != "PROCESSED"
                and new_values["status"] == "PROCESSED"
            )
            else "FAILED"
            if (
                old_values["status"] != "FAILED"
                and new_values["status"] == "FAILED"
            )
            else "UPDATE"
        )

        audit_log = AuditLog(
            user_id=updated_by,
            action=audit_action,
            entity_type="WEBHOOK",
            entity_id=webhook.id,
            old_value=json.dumps(old_values),
            new_value=json.dumps(new_values),
        )

        db.add(audit_log)

    db.commit()
    db.refresh(webhook)

    return webhook


def process_webhook(
    db: Session,
    webhook_id: int,
    processed_by: int | None = None,
) -> Webhook:
    webhook = db.get(
        Webhook,
        webhook_id,
    )

    if not webhook:
        raise ValueError("Webhook not found.")

    if webhook.status == "PROCESSED":
        raise ValueError("Webhook has already been processed.")

    if not webhook.shipment_id:
        webhook.status = "FAILED"
        webhook.error_message = (
            "Webhook is not associated with a shipment."
        )

        db.commit()
        db.refresh(webhook)

        raise ValueError(
            "Webhook is not associated with a shipment."
        )

    shipment = db.get(
        Shipment,
        webhook.shipment_id,
    )

    if not shipment:
        webhook.status = "FAILED"
        webhook.error_message = (
            "Shipment associated with webhook was not found."
        )

        db.commit()
        db.refresh(webhook)

        raise ValueError(
            "Shipment associated with webhook was not found."
        )

    try:
        payload = json.loads(webhook.payload)

    except json.JSONDecodeError:
        webhook.status = "FAILED"
        webhook.error_message = "Invalid JSON payload."

        db.commit()
        db.refresh(webhook)

        raise ValueError("Invalid JSON payload.")

    target_status = payload.get("status")

    if not target_status:
        webhook.status = "FAILED"
        webhook.error_message = (
            "Webhook payload does not contain a status."
        )

        db.commit()
        db.refresh(webhook)

        raise ValueError(
            "Webhook payload does not contain a status."
        )

    try:
        new_status = ShipmentStatus(target_status)

    except ValueError:
        webhook.status = "FAILED"
        webhook.error_message = (
            f"Invalid shipment status: {target_status}"
        )

        db.commit()
        db.refresh(webhook)

        raise ValueError(
            f"Invalid shipment status: {target_status}"
        )

    current_status = ShipmentStatus(shipment.status)

    if current_status != new_status:
        allowed_transitions = {
            ShipmentStatus.CREATED: {
                ShipmentStatus.CONFIRMED,
                ShipmentStatus.CANCELLED,
            },
            ShipmentStatus.CONFIRMED: {
                ShipmentStatus.PICKUP_SCHEDULED,
                ShipmentStatus.CANCELLED,
                ShipmentStatus.ON_HOLD,
            },
            ShipmentStatus.PICKUP_SCHEDULED: {
                ShipmentStatus.PICKED_UP,
                ShipmentStatus.CANCELLED,
                ShipmentStatus.ON_HOLD,
            },
            ShipmentStatus.PICKED_UP: {
                ShipmentStatus.AT_ORIGIN_WAREHOUSE,
                ShipmentStatus.IN_TRANSIT,
                ShipmentStatus.ON_HOLD,
            },
            ShipmentStatus.AT_ORIGIN_WAREHOUSE: {
                ShipmentStatus.IN_TRANSIT,
                ShipmentStatus.ON_HOLD,
            },
            ShipmentStatus.IN_TRANSIT: {
                ShipmentStatus.AT_DESTINATION_WAREHOUSE,
                ShipmentStatus.ON_HOLD,
                ShipmentStatus.LOST,
                ShipmentStatus.DAMAGED,
            },
            ShipmentStatus.AT_DESTINATION_WAREHOUSE: {
                ShipmentStatus.OUT_FOR_DELIVERY,
                ShipmentStatus.ON_HOLD,
            },
            ShipmentStatus.OUT_FOR_DELIVERY: {
                ShipmentStatus.DELIVERED,
                ShipmentStatus.DELIVERY_FAILED,
                ShipmentStatus.ON_HOLD,
            },
            ShipmentStatus.DELIVERY_FAILED: {
                ShipmentStatus.OUT_FOR_DELIVERY,
                ShipmentStatus.RETURN_INITIATED,
            },
            ShipmentStatus.RETURN_INITIATED: {
                ShipmentStatus.RETURNED,
            },
            ShipmentStatus.ON_HOLD: {
                ShipmentStatus.CONFIRMED,
                ShipmentStatus.PICKUP_SCHEDULED,
                ShipmentStatus.PICKED_UP,
                ShipmentStatus.AT_ORIGIN_WAREHOUSE,
                ShipmentStatus.IN_TRANSIT,
                ShipmentStatus.AT_DESTINATION_WAREHOUSE,
                ShipmentStatus.OUT_FOR_DELIVERY,
                ShipmentStatus.CANCELLED,
            },
        }

        allowed = allowed_transitions.get(
            current_status,
            set(),
        )

        if new_status not in allowed:
            webhook.status = "FAILED"
            webhook.error_message = (
                f"Invalid shipment transition: "
                f"{current_status.value} -> {new_status.value}"
            )

            db.commit()
            db.refresh(webhook)

            raise ValueError(
                webhook.error_message
            )

        shipment.status = new_status.value

    location = payload.get("location")
    facility = payload.get("facility")

    description = payload.get(
        "description",
        f"Carrier webhook updated shipment to "
        f"{new_status.value}.",
    )

    tracking_event = TrackingEvent(
        shipment_id=shipment.id,
        status=new_status.value,
        location=location,
        facility=facility,
        description=description,
        source="CARRIER_API",
    )

    db.add(tracking_event)

    # Capture webhook state before processing.
    old_values = {
        "status": webhook.status,
        "processed_at": (
            webhook.processed_at.isoformat()
            if webhook.processed_at
            else None
        ),
        "error_message": webhook.error_message,
    }

    webhook.status = "PROCESSED"
    webhook.processed_at = datetime.utcnow()
    webhook.error_message = None

    new_values = {
        "status": webhook.status,
        "processed_at": (
            webhook.processed_at.isoformat()
            if webhook.processed_at
            else None
        ),
        "error_message": webhook.error_message,
        "shipment_status": new_status.value,
    }

    # Automatic PROCESS audit log.
    audit_log = AuditLog(
        user_id=processed_by,
        action="PROCESS",
        entity_type="WEBHOOK",
        entity_id=webhook.id,
        old_value=json.dumps(old_values),
        new_value=json.dumps(new_values),
    )

    db.add(audit_log)

    db.commit()
    db.refresh(webhook)

    # Automatically notify customer after successful webhook processing.
    if (
        shipment.order is not None
        and shipment.order.customer is not None
    ):
        customer_user_id = shipment.order.customer.user_id

        notification_message = (
            f"Shipment {shipment.shipment_number} status was updated "
            f"to {new_status.value} by the carrier webhook."
        )

        create_and_dispatch_shipment_notification(
            db=db,
            shipment_id=shipment.id,
            user_id=customer_user_id,
            status=new_status.value,
            message=notification_message,
        )

    return webhook