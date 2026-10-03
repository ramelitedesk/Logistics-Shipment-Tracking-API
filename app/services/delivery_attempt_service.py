import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.delivery_agent import DeliveryAgent
from app.models.delivery_attempt import DeliveryAttempt
from app.models.shipment import Shipment
from app.models.shipment_assignment import ShipmentAssignment
from app.schemas.delivery_attempt import (
    DeliveryAttemptCreate,
    DeliveryAttemptUpdate,
)
from app.services.notification_automation_service import (
    create_and_dispatch_shipment_notification,
)


def create_delivery_attempt(
    db: Session,
    attempt_data: DeliveryAttemptCreate,
    created_by: int | None = None,
) -> DeliveryAttempt:
    # 1. Validate shipment
    shipment = db.get(
        Shipment,
        attempt_data.shipment_id,
    )

    if not shipment:
        raise ValueError("Shipment not found.")

    # 2. Validate delivery agent
    delivery_agent = db.get(
        DeliveryAgent,
        attempt_data.delivery_agent_id,
    )

    if not delivery_agent:
        raise ValueError("Delivery agent not found.")

    if not delivery_agent.is_active:
        raise ValueError(
            "Cannot create a delivery attempt for an inactive delivery agent."
        )

    # 3. Validate shipment assignment
    assignment = db.scalar(
        select(ShipmentAssignment).where(
            ShipmentAssignment.shipment_id
            == attempt_data.shipment_id,
            ShipmentAssignment.delivery_agent_id
            == attempt_data.delivery_agent_id,
            ShipmentAssignment.is_active.is_(True),
        )
    )

    if not assignment:
        raise ValueError(
            "Delivery agent is not actively assigned to this shipment."
        )

    # 4. Calculate attempt number automatically
    last_attempt_number = db.scalar(
        select(DeliveryAttempt.attempt_number)
        .where(
            DeliveryAttempt.shipment_id
            == attempt_data.shipment_id
        )
        .order_by(
            DeliveryAttempt.attempt_number.desc()
        )
        .limit(1)
    )

    attempt_number = (
        last_attempt_number + 1
        if last_attempt_number is not None
        else 1
    )

    # 5. Validate failure reason
    if (
        attempt_data.status.value == "FAILED"
        and not attempt_data.failure_reason
    ):
        raise ValueError(
            "Failure reason is required for a failed delivery attempt."
        )

    # 6. Create delivery attempt
    attempt = DeliveryAttempt(
        shipment_id=attempt_data.shipment_id,
        delivery_agent_id=attempt_data.delivery_agent_id,
        attempt_number=attempt_number,
        status=attempt_data.status.value,
        failure_reason=attempt_data.failure_reason,
        notes=attempt_data.notes,
    )

    db.add(attempt)

    # Get generated ID before creating audit log
    db.flush()

    # 7. Automatic audit log
    audit_log = AuditLog(
        user_id=created_by,
        action="CREATE",
        entity_type="DELIVERY_ATTEMPT",
        entity_id=attempt.id,
        old_value=None,
        new_value=json.dumps(
            {
                "shipment_id": attempt.shipment_id,
                "delivery_agent_id": attempt.delivery_agent_id,
                "attempt_number": attempt.attempt_number,
                "status": attempt.status,
                "failure_reason": attempt.failure_reason,
                "notes": attempt.notes,
            }
        ),
    )

    db.add(audit_log)

    # 8. Commit delivery attempt
    db.commit()
    db.refresh(attempt)

    # 9. Automatically notify customer after successful delivery
    if (
        attempt.status == "SUCCESS"
        and shipment.order is not None
        and shipment.order.customer is not None
    ):
        customer_user_id = shipment.order.customer.user_id

        notification_message = (
            f"Shipment {shipment.shipment_number} "
            f"was successfully delivered."
        )

        create_and_dispatch_shipment_notification(
            db=db,
            shipment_id=shipment.id,
            user_id=customer_user_id,
            status="DELIVERED",
            message=notification_message,
        )

    return attempt


def get_delivery_attempt(
    db: Session,
    attempt_id: int,
) -> DeliveryAttempt | None:
    return db.get(
        DeliveryAttempt,
        attempt_id,
    )


def get_delivery_attempts(
    db: Session,
) -> list[DeliveryAttempt]:
    return list(
        db.scalars(
            select(DeliveryAttempt).order_by(
                DeliveryAttempt.id.desc()
            )
        ).all()
    )


def get_attempts_by_shipment(
    db: Session,
    shipment_id: int,
) -> list[DeliveryAttempt]:
    return list(
        db.scalars(
            select(DeliveryAttempt)
            .where(
                DeliveryAttempt.shipment_id == shipment_id
            )
            .order_by(
                DeliveryAttempt.attempt_number.asc()
            )
        ).all()
    )


def update_delivery_attempt(
    db: Session,
    attempt_id: int,
    attempt_data: DeliveryAttemptUpdate,
    updated_by: int | None = None,
) -> DeliveryAttempt | None:
    attempt = db.get(
        DeliveryAttempt,
        attempt_id,
    )

    if not attempt:
        return None

    # Store original values
    old_values = {
        "status": attempt.status,
        "failure_reason": attempt.failure_reason,
        "notes": attempt.notes,
    }

    # Update status
    if attempt_data.status is not None:
        attempt.status = attempt_data.status.value

    # Update failure reason
    if attempt_data.failure_reason is not None:
        attempt.failure_reason = attempt_data.failure_reason

    # Update notes
    if attempt_data.notes is not None:
        attempt.notes = attempt_data.notes

    # Ensure FAILED attempts have a reason
    if (
        attempt.status == "FAILED"
        and not attempt.failure_reason
    ):
        raise ValueError(
            "Failure reason is required for a failed delivery attempt."
        )

    # New values
    new_values = {
        "status": attempt.status,
        "failure_reason": attempt.failure_reason,
        "notes": attempt.notes,
    }

    # Create audit log only if something changed
    if old_values != new_values:
        audit_log = AuditLog(
            user_id=updated_by,
            action="UPDATE",
            entity_type="DELIVERY_ATTEMPT",
            entity_id=attempt.id,
            old_value=json.dumps(old_values),
            new_value=json.dumps(new_values),
        )

        db.add(audit_log)

    # Store whether the attempt became successful
    became_successful = (
        old_values["status"] != "SUCCESS"
        and attempt.status == "SUCCESS"
    )

    db.commit()
    db.refresh(attempt)

    # Automatically notify customer after successful delivery
    if became_successful:
        shipment = db.get(
            Shipment,
            attempt.shipment_id,
        )

        if (
            shipment is not None
            and shipment.order is not None
            and shipment.order.customer is not None
        ):
            customer_user_id = shipment.order.customer.user_id

            notification_message = (
                f"Shipment {shipment.shipment_number} "
                f"was successfully delivered."
            )

            create_and_dispatch_shipment_notification(
                db=db,
                shipment_id=shipment.id,
                user_id=customer_user_id,
                status="DELIVERED",
                message=notification_message,
            )

    return attempt