import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.shipment_status import ShipmentStatus
from app.models.audit_log import AuditLog
from app.models.shipment import Shipment
from app.models.tracking_event import TrackingEvent
from app.models.warehouse import Warehouse
from app.schemas.shipment import ShipmentCreate, ShipmentUpdate
from app.services.notification_automation_service import (
    create_and_dispatch_shipment_notification,
)


def create_shipment(
    db: Session,
    shipment_data: ShipmentCreate,
) -> Shipment:
    existing_shipment = db.execute(
        select(Shipment).where(
            Shipment.shipment_number == shipment_data.shipment_number
        )
    ).scalar_one_or_none()

    if existing_shipment is not None:
        raise ValueError("Shipment number already exists")

    if shipment_data.tracking_number is not None:
        existing_tracking = db.execute(
            select(Shipment).where(
                Shipment.tracking_number == shipment_data.tracking_number
            )
        ).scalar_one_or_none()

        if existing_tracking is not None:
            raise ValueError("Tracking number already exists")

    if shipment_data.origin_warehouse_id is not None:
        origin_warehouse = db.execute(
            select(Warehouse).where(
                Warehouse.id == shipment_data.origin_warehouse_id
            )
        ).scalar_one_or_none()

        if origin_warehouse is None:
            raise ValueError("Origin warehouse not found")

        if not origin_warehouse.is_active:
            raise ValueError("Origin warehouse is inactive")

    if shipment_data.destination_warehouse_id is not None:
        destination_warehouse = db.execute(
            select(Warehouse).where(
                Warehouse.id == shipment_data.destination_warehouse_id
            )
        ).scalar_one_or_none()

        if destination_warehouse is None:
            raise ValueError("Destination warehouse not found")

        if not destination_warehouse.is_active:
            raise ValueError("Destination warehouse is inactive")

    shipment = Shipment(
        order_id=shipment_data.order_id,
        shipment_number=shipment_data.shipment_number,
        tracking_number=shipment_data.tracking_number,
        origin_warehouse_id=shipment_data.origin_warehouse_id,
        destination_warehouse_id=shipment_data.destination_warehouse_id,
        status=ShipmentStatus.CREATED.value,
    )

    db.add(shipment)
    db.commit()
    db.refresh(shipment)

    return shipment


def get_shipment_by_id(
    db: Session,
    shipment_id: int,
) -> Shipment | None:
    return db.execute(
        select(Shipment).where(
            Shipment.id == shipment_id
        )
    ).scalar_one_or_none()


def get_shipments(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Shipment]:
    result = db.execute(
        select(Shipment)
        .order_by(Shipment.id.desc())
        .offset(skip)
        .limit(limit)
    )

    return list(result.scalars().all())


def get_shipments_by_order(
    db: Session,
    order_id: int,
) -> list[Shipment]:
    result = db.execute(
        select(Shipment)
        .where(Shipment.order_id == order_id)
        .order_by(Shipment.id.desc())
    )

    return list(result.scalars().all())


def update_shipment(
    db: Session,
    shipment_id: int,
    shipment_data: ShipmentUpdate,
    updated_by: int | None = None,
) -> Shipment | None:
    shipment = get_shipment_by_id(
        db=db,
        shipment_id=shipment_id,
    )

    if shipment is None:
        return None

    update_data = shipment_data.model_dump(
        exclude_unset=True,
    )

    # ---------------------------------------------------------
    # Store original values for audit logging
    # ---------------------------------------------------------

    original_values = {}

    for field in update_data:
        if field == "status":
            original_values[field] = shipment.status

        elif field == "tracking_number":
            original_values[field] = shipment.tracking_number

        elif field == "origin_warehouse_id":
            original_values[field] = shipment.origin_warehouse_id

        elif field == "destination_warehouse_id":
            original_values[field] = shipment.destination_warehouse_id

    # ---------------------------------------------------------
    # Tracking number validation
    # ---------------------------------------------------------

    if "tracking_number" in update_data:
        new_tracking_number = update_data["tracking_number"]

        if (
            new_tracking_number is not None
            and new_tracking_number != shipment.tracking_number
        ):
            existing_tracking = db.execute(
                select(Shipment).where(
                    Shipment.tracking_number == new_tracking_number,
                    Shipment.id != shipment_id,
                )
            ).scalar_one_or_none()

            if existing_tracking is not None:
                raise ValueError("Tracking number already exists")

    # ---------------------------------------------------------
    # Origin warehouse validation
    # ---------------------------------------------------------

    if "origin_warehouse_id" in update_data:
        origin_warehouse_id = update_data[
            "origin_warehouse_id"
        ]

        if origin_warehouse_id is not None:
            origin_warehouse = db.execute(
                select(Warehouse).where(
                    Warehouse.id == origin_warehouse_id
                )
            ).scalar_one_or_none()

            if origin_warehouse is None:
                raise ValueError("Origin warehouse not found")

            if not origin_warehouse.is_active:
                raise ValueError("Origin warehouse is inactive")

    # ---------------------------------------------------------
    # Destination warehouse validation
    # ---------------------------------------------------------

    if "destination_warehouse_id" in update_data:
        destination_warehouse_id = update_data[
            "destination_warehouse_id"
        ]

        if destination_warehouse_id is not None:
            destination_warehouse = db.execute(
                select(Warehouse).where(
                    Warehouse.id == destination_warehouse_id
                )
            ).scalar_one_or_none()

            if destination_warehouse is None:
                raise ValueError("Destination warehouse not found")

            if not destination_warehouse.is_active:
                raise ValueError("Destination warehouse is inactive")

    # ---------------------------------------------------------
    # Shipment status validation + tracking event
    # ---------------------------------------------------------

    status_changed = False
    old_status = None
    new_status_value = None

    if "status" in update_data:
        new_status = update_data["status"]

        if new_status is not None:
            current_status = ShipmentStatus(
                shipment.status
            )

            if new_status != current_status:
                from app.core.shipment_workflow import (
                    ALLOWED_SHIPMENT_TRANSITIONS,
                )

                allowed_statuses = ALLOWED_SHIPMENT_TRANSITIONS.get(
                    current_status,
                    set(),
                )

                if new_status not in allowed_statuses:
                    raise ValueError(
                        f"Invalid shipment status transition: "
                        f"{current_status.value} -> "
                        f"{new_status.value}"
                    )

                old_status = current_status.value
                new_status_value = new_status.value
                status_changed = True

                shipment.status = new_status.value

                # Existing tracking event functionality
                tracking_event = TrackingEvent(
                    shipment_id=shipment.id,
                    status=new_status.value,
                    description=(
                        f"Shipment status changed from "
                        f"{current_status.value} to "
                        f"{new_status.value}"
                    ),
                    created_by=updated_by,
                    source="SYSTEM",
                )

                db.add(tracking_event)

    # ---------------------------------------------------------
    # Apply remaining shipment updates
    # ---------------------------------------------------------

    for field, value in update_data.items():
        if field == "status":
            continue

        setattr(shipment, field, value)

    # ---------------------------------------------------------
    # Automatic Audit Logging
    # ---------------------------------------------------------

    for field, old_value in original_values.items():
        new_value = getattr(shipment, field)

        if old_value != new_value:
            audit_log = AuditLog(
                user_id=updated_by,
                action="UPDATE",
                entity_type="SHIPMENT",
                entity_id=shipment.id,
                old_value=json.dumps(
                    {
                        field: old_value,
                    }
                ),
                new_value=json.dumps(
                    {
                        field: new_value,
                    }
                ),
            )

            db.add(audit_log)

    # ---------------------------------------------------------
    # Commit shipment changes first
    # ---------------------------------------------------------

    db.commit()
    db.refresh(shipment)

    # ---------------------------------------------------------
    # Automatic Shipment Notification
    # ---------------------------------------------------------

    if (
        status_changed
        and new_status_value is not None
        and shipment.order is not None
        and shipment.order.customer is not None
    ):
        customer_user_id = shipment.order.customer.user_id

        notification_message = (
            f"Shipment {shipment.shipment_number} "
            f"status changed from {old_status} "
            f"to {new_status_value}."
        )

        create_and_dispatch_shipment_notification(
            db=db,
            shipment_id=shipment.id,
            user_id=customer_user_id,
            status=new_status_value,
            message=notification_message,
        )

    return shipment