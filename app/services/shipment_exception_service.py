import json
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.shipment import Shipment
from app.models.shipment_exception import ShipmentException
from app.models.user import User
from app.schemas.shipment_exception import (
    ShipmentExceptionCreate,
    ShipmentExceptionUpdate,
)
from app.services.notification_automation_service import (
    create_and_dispatch_shipment_notification,
)


def create_shipment_exception(
    db: Session,
    exception_data: ShipmentExceptionCreate,
    reported_by: int,
) -> ShipmentException:
    # 1. Validate shipment
    shipment = db.get(
        Shipment,
        exception_data.shipment_id,
    )

    if not shipment:
        raise ValueError("Shipment not found.")

    # 2. Validate reporting user
    user = db.get(
        User,
        reported_by,
    )

    if not user:
        raise ValueError("Reporting user not found.")

    # 3. Prevent invalid resolution data on creation
    if (
        exception_data.status.value == "RESOLVED"
        and not exception_data.resolution_notes
    ):
        raise ValueError(
            "Resolution notes are required when creating a resolved exception."
        )

    # 4. Set resolved timestamp automatically
    resolved_at = (
        datetime.utcnow()
        if exception_data.status.value == "RESOLVED"
        else None
    )

    # 5. Create exception
    shipment_exception = ShipmentException(
        shipment_id=exception_data.shipment_id,
        exception_type=exception_data.exception_type.value,
        description=exception_data.description,
        reported_by=reported_by,
        status=exception_data.status.value,
        resolved_at=resolved_at,
        resolution_notes=exception_data.resolution_notes,
    )

    db.add(shipment_exception)

    # Generate ID before creating audit log
    db.flush()

    # 6. Create automatic audit log
    audit_log = AuditLog(
        user_id=reported_by,
        action="CREATE",
        entity_type="SHIPMENT_EXCEPTION",
        entity_id=shipment_exception.id,
        old_value=None,
        new_value=json.dumps(
            {
                "shipment_id": shipment_exception.shipment_id,
                "exception_type": shipment_exception.exception_type,
                "description": shipment_exception.description,
                "reported_by": shipment_exception.reported_by,
                "status": shipment_exception.status,
                "resolved_at": (
                    shipment_exception.resolved_at.isoformat()
                    if shipment_exception.resolved_at
                    else None
                ),
                "resolution_notes": shipment_exception.resolution_notes,
            }
        ),
    )

    db.add(audit_log)

    # 7. Commit exception
    db.commit()
    db.refresh(shipment_exception)

    # 8. Notify customer about the new exception
    if (
        shipment.order is not None
        and shipment.order.customer is not None
    ):
        customer_user_id = shipment.order.customer.user_id

        notification_message = (
            f"Shipment {shipment.shipment_number} has a "
            f"{shipment_exception.exception_type} exception. "
            f"{shipment_exception.description}"
        )

        create_and_dispatch_shipment_notification(
            db=db,
            shipment_id=shipment.id,
            user_id=customer_user_id,
            status="EXCEPTION",
            message=notification_message,
        )

    return shipment_exception


def get_shipment_exception(
    db: Session,
    exception_id: int,
) -> ShipmentException | None:
    return db.get(
        ShipmentException,
        exception_id,
    )


def get_shipment_exceptions(
    db: Session,
) -> list[ShipmentException]:
    return list(
        db.scalars(
            select(ShipmentException).order_by(
                ShipmentException.id.desc()
            )
        ).all()
    )


def get_exceptions_by_shipment(
    db: Session,
    shipment_id: int,
) -> list[ShipmentException]:
    return list(
        db.scalars(
            select(ShipmentException)
            .where(
                ShipmentException.shipment_id == shipment_id
            )
            .order_by(
                ShipmentException.id.desc()
            )
        ).all()
    )


def update_shipment_exception(
    db: Session,
    exception_id: int,
    exception_data: ShipmentExceptionUpdate,
    updated_by: int | None = None,
) -> ShipmentException | None:
    shipment_exception = db.get(
        ShipmentException,
        exception_id,
    )

    if not shipment_exception:
        return None

    # Capture old values before modification
    old_values = {
        "exception_type": shipment_exception.exception_type,
        "description": shipment_exception.description,
        "status": shipment_exception.status,
        "resolved_at": (
            shipment_exception.resolved_at.isoformat()
            if shipment_exception.resolved_at
            else None
        ),
        "resolution_notes": shipment_exception.resolution_notes,
    }

    # Track whether exception becomes resolved
    became_resolved = False

    # Update exception type
    if exception_data.exception_type is not None:
        shipment_exception.exception_type = (
            exception_data.exception_type.value
        )

    # Update description
    if exception_data.description is not None:
        shipment_exception.description = (
            exception_data.description
        )

    # Update resolution notes
    if exception_data.resolution_notes is not None:
        shipment_exception.resolution_notes = (
            exception_data.resolution_notes
        )

    # Update status
    if exception_data.status is not None:
        new_status = exception_data.status.value

        # Resolve exception
        if new_status == "RESOLVED":
            if not shipment_exception.resolution_notes:
                raise ValueError(
                    "Resolution notes are required when resolving an exception."
                )

            if shipment_exception.status != "RESOLVED":
                became_resolved = True

            shipment_exception.status = "RESOLVED"

            if shipment_exception.resolved_at is None:
                shipment_exception.resolved_at = datetime.utcnow()

        # Re-open exception
        elif new_status == "OPEN":
            shipment_exception.status = "OPEN"
            shipment_exception.resolved_at = None

    # Capture new values
    new_values = {
        "exception_type": shipment_exception.exception_type,
        "description": shipment_exception.description,
        "status": shipment_exception.status,
        "resolved_at": (
            shipment_exception.resolved_at.isoformat()
            if shipment_exception.resolved_at
            else None
        ),
        "resolution_notes": shipment_exception.resolution_notes,
    }

    # Create audit log only when something changed
    if old_values != new_values:
        audit_action = "RESOLVE" if (
            old_values["status"] != "RESOLVED"
            and new_values["status"] == "RESOLVED"
        ) else "UPDATE"

        audit_log = AuditLog(
            user_id=updated_by,
            action=audit_action,
            entity_type="SHIPMENT_EXCEPTION",
            entity_id=shipment_exception.id,
            old_value=json.dumps(old_values),
            new_value=json.dumps(new_values),
        )

        db.add(audit_log)

    # Commit exception update
    db.commit()
    db.refresh(shipment_exception)

    # Notify customer only when exception becomes RESOLVED
    if became_resolved:
        shipment = db.get(
            Shipment,
            shipment_exception.shipment_id,
        )

        if (
            shipment
            and shipment.order is not None
            and shipment.order.customer is not None
        ):
            customer_user_id = shipment.order.customer.user_id

            notification_message = (
                f"Shipment {shipment.shipment_number} exception "
                f"{shipment_exception.exception_type} has been resolved. "
                f"Resolution: "
                f"{shipment_exception.resolution_notes}"
            )

            create_and_dispatch_shipment_notification(
                db=db,
                shipment_id=shipment.id,
                user_id=customer_user_id,
                status="EXCEPTION_RESOLVED",
                message=notification_message,
            )

    return shipment_exception