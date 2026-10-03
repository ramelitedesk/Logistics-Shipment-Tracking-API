import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.delivery_attempt import DeliveryAttempt
from app.models.proof_of_delivery import ProofOfDelivery
from app.models.shipment import Shipment
from app.schemas.proof_of_delivery import (
    ProofOfDeliveryCreate,
    ProofOfDeliveryUpdate,
)
from app.services.notification_automation_service import (
    create_and_dispatch_shipment_notification,
)


def create_proof_of_delivery(
    db: Session,
    pod_data: ProofOfDeliveryCreate,
    created_by: int | None = None,
) -> ProofOfDelivery:
    # 1. Validate shipment
    shipment = db.get(
        Shipment,
        pod_data.shipment_id,
    )

    if not shipment:
        raise ValueError("Shipment not found.")

    # 2. Validate delivery attempt
    delivery_attempt = db.get(
        DeliveryAttempt,
        pod_data.delivery_attempt_id,
    )

    if not delivery_attempt:
        raise ValueError("Delivery attempt not found.")

    # 3. Ensure the attempt belongs to the shipment
    if delivery_attempt.shipment_id != pod_data.shipment_id:
        raise ValueError(
            "Delivery attempt does not belong to this shipment."
        )

    # 4. POD can only be created for a successful attempt
    if delivery_attempt.status != "SUCCESS":
        raise ValueError(
            "Proof of delivery can only be created for a successful delivery attempt."
        )

    # 5. Ensure shipment does not already have POD
    existing_pod = db.scalar(
        select(ProofOfDelivery).where(
            ProofOfDelivery.shipment_id
            == pod_data.shipment_id
        )
    )

    if existing_pod:
        raise ValueError(
            "Proof of delivery already exists for this shipment."
        )

    # 6. Ensure attempt does not already have POD
    existing_attempt_pod = db.scalar(
        select(ProofOfDelivery).where(
            ProofOfDelivery.delivery_attempt_id
            == pod_data.delivery_attempt_id
        )
    )

    if existing_attempt_pod:
        raise ValueError(
            "Proof of delivery already exists for this delivery attempt."
        )

    # 7. Create POD
    pod = ProofOfDelivery(
        shipment_id=pod_data.shipment_id,
        delivery_attempt_id=pod_data.delivery_attempt_id,
        recipient_name=pod_data.recipient_name,
        signature_reference=pod_data.signature_reference,
        photo_reference=pod_data.photo_reference,
        notes=pod_data.notes,
    )

    db.add(pod)

    # Generate POD ID before creating audit log
    db.flush()

    # 8. Create automatic audit log
    audit_log = AuditLog(
        user_id=created_by,
        action="CREATE",
        entity_type="PROOF_OF_DELIVERY",
        entity_id=pod.id,
        old_value=None,
        new_value=json.dumps(
            {
                "shipment_id": pod.shipment_id,
                "delivery_attempt_id": pod.delivery_attempt_id,
                "recipient_name": pod.recipient_name,
                "signature_reference": pod.signature_reference,
                "photo_reference": pod.photo_reference,
                "notes": pod.notes,
            }
        ),
    )

    db.add(audit_log)

    # 9. Commit POD
    db.commit()
    db.refresh(pod)

    # 10. Automatically notify customer
    if (
        shipment.order is not None
        and shipment.order.customer is not None
    ):
        customer_user_id = shipment.order.customer.user_id

        notification_message = (
            f"Proof of delivery has been recorded for "
            f"shipment {shipment.shipment_number}. "
            f"Recipient: {pod.recipient_name}."
        )

        create_and_dispatch_shipment_notification(
            db=db,
            shipment_id=shipment.id,
            user_id=customer_user_id,
            status="DELIVERED",
            message=notification_message,
        )

    return pod


def get_proof_of_delivery(
    db: Session,
    pod_id: int,
) -> ProofOfDelivery | None:
    return db.get(
        ProofOfDelivery,
        pod_id,
    )


def get_proof_of_delivery_by_shipment(
    db: Session,
    shipment_id: int,
) -> ProofOfDelivery | None:
    return db.scalar(
        select(ProofOfDelivery).where(
            ProofOfDelivery.shipment_id == shipment_id
        )
    )


def get_proof_of_deliveries(
    db: Session,
) -> list[ProofOfDelivery]:
    return list(
        db.scalars(
            select(ProofOfDelivery).order_by(
                ProofOfDelivery.id.desc()
            )
        ).all()
    )


def update_proof_of_delivery(
    db: Session,
    pod_id: int,
    pod_data: ProofOfDeliveryUpdate,
    updated_by: int | None = None,
) -> ProofOfDelivery | None:
    pod = db.get(
        ProofOfDelivery,
        pod_id,
    )

    if not pod:
        return None

    # Capture old values before modification
    old_values = {
        "recipient_name": pod.recipient_name,
        "signature_reference": pod.signature_reference,
        "photo_reference": pod.photo_reference,
        "notes": pod.notes,
    }

    # Apply updates
    if pod_data.recipient_name is not None:
        pod.recipient_name = pod_data.recipient_name

    if pod_data.signature_reference is not None:
        pod.signature_reference = pod_data.signature_reference

    if pod_data.photo_reference is not None:
        pod.photo_reference = pod_data.photo_reference

    if pod_data.notes is not None:
        pod.notes = pod_data.notes

    # Capture new values
    new_values = {
        "recipient_name": pod.recipient_name,
        "signature_reference": pod.signature_reference,
        "photo_reference": pod.photo_reference,
        "notes": pod.notes,
    }

    # Only create audit log if something actually changed
    if old_values != new_values:
        audit_log = AuditLog(
            user_id=updated_by,
            action="UPDATE",
            entity_type="PROOF_OF_DELIVERY",
            entity_id=pod.id,
            old_value=json.dumps(old_values),
            new_value=json.dumps(new_values),
        )

        db.add(audit_log)

    db.commit()
    db.refresh(pod)

    return pod