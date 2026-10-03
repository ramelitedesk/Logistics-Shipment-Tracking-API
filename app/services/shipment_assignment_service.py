import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.delivery_agent import DeliveryAgent
from app.models.shipment import Shipment
from app.models.shipment_assignment import ShipmentAssignment
from app.schemas.shipment_assignment import (
    ShipmentAssignmentCreate,
    ShipmentAssignmentUpdate,
)


def create_shipment_assignment(
    db: Session,
    assignment_data: ShipmentAssignmentCreate,
    created_by: int | None = None,
) -> ShipmentAssignment:
    # Verify shipment exists
    shipment = db.get(
        Shipment,
        assignment_data.shipment_id,
    )

    if not shipment:
        raise ValueError("Shipment not found.")

    # Verify delivery agent exists
    delivery_agent = db.get(
        DeliveryAgent,
        assignment_data.delivery_agent_id,
    )

    if not delivery_agent:
        raise ValueError("Delivery agent not found.")

    # Delivery agent must be active
    if not delivery_agent.is_active:
        raise ValueError(
            "Cannot assign an inactive delivery agent."
        )

    # Only one assignment per shipment
    existing_assignment = db.scalar(
        select(ShipmentAssignment).where(
            ShipmentAssignment.shipment_id
            == assignment_data.shipment_id
        )
    )

    if existing_assignment:
        raise ValueError(
            "Shipment already has a delivery agent assignment."
        )

    assignment = ShipmentAssignment(
        shipment_id=assignment_data.shipment_id,
        delivery_agent_id=assignment_data.delivery_agent_id,
        is_active=True,
    )

    db.add(assignment)
    db.flush()

    # Automatic audit log
    audit_log = AuditLog(
        user_id=created_by,
        action="CREATE",
        entity_type="SHIPMENT_ASSIGNMENT",
        entity_id=assignment.id,
        old_value=None,
        new_value=json.dumps(
            {
                "shipment_id": assignment.shipment_id,
                "delivery_agent_id": assignment.delivery_agent_id,
                "is_active": assignment.is_active,
            }
        ),
    )

    db.add(audit_log)

    db.commit()
    db.refresh(assignment)

    return assignment


def get_shipment_assignment(
    db: Session,
    assignment_id: int,
) -> ShipmentAssignment | None:
    return db.get(
        ShipmentAssignment,
        assignment_id,
    )


def get_assignment_by_shipment(
    db: Session,
    shipment_id: int,
) -> ShipmentAssignment | None:
    return db.scalar(
        select(ShipmentAssignment).where(
            ShipmentAssignment.shipment_id == shipment_id
        )
    )


def get_assignments(
    db: Session,
) -> list[ShipmentAssignment]:
    return list(
        db.scalars(
            select(ShipmentAssignment).order_by(
                ShipmentAssignment.id.desc()
            )
        ).all()
    )


def update_shipment_assignment(
    db: Session,
    assignment_id: int,
    assignment_data: ShipmentAssignmentUpdate,
    updated_by: int | None = None,
) -> ShipmentAssignment | None:
    assignment = db.get(
        ShipmentAssignment,
        assignment_id,
    )

    if not assignment:
        return None

    # Store original values for audit
    old_values = {
        "delivery_agent_id": assignment.delivery_agent_id,
        "is_active": assignment.is_active,
    }

    # Verify new delivery agent
    delivery_agent = db.get(
        DeliveryAgent,
        assignment_data.delivery_agent_id,
    )

    if not delivery_agent:
        raise ValueError("Delivery agent not found.")

    if not delivery_agent.is_active:
        raise ValueError(
            "Cannot assign an inactive delivery agent."
        )

    # If changing agent, make sure the shipment is not
    # already assigned to another assignment record.
    if (
        assignment.delivery_agent_id
        != assignment_data.delivery_agent_id
    ):
        existing_assignment = db.scalar(
            select(ShipmentAssignment).where(
                ShipmentAssignment.shipment_id
                == assignment.shipment_id,
                ShipmentAssignment.id != assignment.id,
            )
        )

        if existing_assignment:
            raise ValueError(
                "Shipment already has another delivery agent assignment."
            )

    assignment.delivery_agent_id = (
        assignment_data.delivery_agent_id
    )

    if assignment_data.is_active is not None:
        assignment.is_active = assignment_data.is_active

    # Create audit log only when something actually changed
    new_values = {
        "delivery_agent_id": assignment.delivery_agent_id,
        "is_active": assignment.is_active,
    }

    if old_values != new_values:
        audit_log = AuditLog(
            user_id=updated_by,
            action="UPDATE",
            entity_type="SHIPMENT_ASSIGNMENT",
            entity_id=assignment.id,
            old_value=json.dumps(old_values),
            new_value=json.dumps(new_values),
        )

        db.add(audit_log)

    db.commit()
    db.refresh(assignment)

    return assignment