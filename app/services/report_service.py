from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.carrier import Carrier
from app.models.delivery_attempt import DeliveryAttempt
from app.models.shipment import Shipment
from app.models.shipment_exception import ShipmentException


def get_shipment_summary(db: Session) -> dict:
    total_shipments = db.scalar(
        select(func.count(Shipment.id))
    ) or 0

    status_counts = db.execute(
        select(
            Shipment.status,
            func.count(Shipment.id)
        ).group_by(Shipment.status)
    ).all()

    counts = {
        str(status): count
        for status, count in status_counts
    }

    total_exceptions = db.scalar(
        select(func.count(ShipmentException.id))
    ) or 0

    return {
        "total_shipments": total_shipments,
        "created": counts.get("CREATED", 0),
        "confirmed": counts.get("CONFIRMED", 0),
        "pickup_scheduled": counts.get("PICKUP_SCHEDULED", 0),
        "picked_up": counts.get("PICKED_UP", 0),
        "at_origin_warehouse": counts.get("AT_ORIGIN_WAREHOUSE", 0),
        "in_transit": counts.get("IN_TRANSIT", 0),
        "at_destination_warehouse": counts.get(
            "AT_DESTINATION_WAREHOUSE", 0
        ),
        "out_for_delivery": counts.get("OUT_FOR_DELIVERY", 0),
        "delivered": counts.get("DELIVERED", 0),
        "cancelled": counts.get("CANCELLED", 0),
        "on_hold": counts.get("ON_HOLD", 0),
        "delivery_failed": counts.get("DELIVERY_FAILED", 0),
        "return_initiated": counts.get("RETURN_INITIATED", 0),
        "returned": counts.get("RETURNED", 0),
        "lost": counts.get("LOST", 0),
        "damaged": counts.get("DAMAGED", 0),
        "total_exceptions": total_exceptions,
    }


def get_delivery_performance(db: Session) -> dict:
    total_attempts = db.scalar(
        select(func.count(DeliveryAttempt.id))
    ) or 0

    successful_attempts = db.scalar(
        select(func.count(DeliveryAttempt.id))
        .where(DeliveryAttempt.status == "SUCCESS")
    ) or 0

    failed_attempts = db.scalar(
        select(func.count(DeliveryAttempt.id))
        .where(DeliveryAttempt.status == "FAILED")
    ) or 0

    rescheduled_attempts = db.scalar(
        select(func.count(DeliveryAttempt.id))
        .where(DeliveryAttempt.status == "RESCHEDULED")
    ) or 0

    if total_attempts:
        success_rate = round(
            (successful_attempts / total_attempts) * 100,
            2,
        )

        failure_rate = round(
            (failed_attempts / total_attempts) * 100,
            2,
        )

        reschedule_rate = round(
            (rescheduled_attempts / total_attempts) * 100,
            2,
        )
    else:
        success_rate = 0.0
        failure_rate = 0.0
        reschedule_rate = 0.0

    return {
        "total_attempts": total_attempts,
        "successful_attempts": successful_attempts,
        "failed_attempts": failed_attempts,
        "rescheduled_attempts": rescheduled_attempts,
        "success_rate": success_rate,
        "failure_rate": failure_rate,
        "reschedule_rate": reschedule_rate,
    }


def get_carrier_performance(db: Session) -> list[dict]:
    rows = db.execute(
        select(
            Carrier.id,
            Carrier.name,
            func.count(Shipment.id),
            func.count(Shipment.id).filter(
                Shipment.status == "DELIVERED"
            ),
            func.count(Shipment.id).filter(
                Shipment.status == "DELIVERY_FAILED"
            ),
        )
        .outerjoin(
            Shipment,
            Shipment.carrier_id == Carrier.id,
        )
        .group_by(
            Carrier.id,
            Carrier.name,
        )
        .order_by(Carrier.id)
    ).all()

    results = []

    for (
        carrier_id,
        carrier_name,
        total_shipments,
        delivered_shipments,
        failed_shipments,
    ) in rows:
        delivered_rate = (
            round(
                (delivered_shipments / total_shipments) * 100,
                2,
            )
            if total_shipments
            else 0.0
        )

        results.append(
            {
                "carrier_id": carrier_id,
                "carrier_name": carrier_name,
                "total_shipments": total_shipments,
                "delivered_shipments": delivered_shipments,
                "failed_shipments": failed_shipments,
                "delivered_rate": delivered_rate,
            }
        )

    return results

def get_exception_report(db: Session) -> dict:
    total_exceptions = db.scalar(
        select(func.count(ShipmentException.id))
    ) or 0

    open_exceptions = db.scalar(
        select(func.count(ShipmentException.id))
        .where(ShipmentException.status == "OPEN")
    ) or 0

    resolved_exceptions = db.scalar(
        select(func.count(ShipmentException.id))
        .where(ShipmentException.status == "RESOLVED")
    ) or 0

    damaged = db.scalar(
        select(func.count(ShipmentException.id))
        .where(ShipmentException.exception_type == "DAMAGED")
    ) or 0

    lost = db.scalar(
        select(func.count(ShipmentException.id))
        .where(ShipmentException.exception_type == "LOST")
    ) or 0

    address_issue = db.scalar(
        select(func.count(ShipmentException.id))
        .where(ShipmentException.exception_type == "ADDRESS_ISSUE")
    ) or 0

    customer_unavailable = db.scalar(
        select(func.count(ShipmentException.id))
        .where(
            ShipmentException.exception_type
            == "CUSTOMER_UNAVAILABLE"
        )
    ) or 0

    weather_delay = db.scalar(
        select(func.count(ShipmentException.id))
        .where(
            ShipmentException.exception_type
            == "WEATHER_DELAY"
        )
    ) or 0

    other = db.scalar(
        select(func.count(ShipmentException.id))
        .where(ShipmentException.exception_type == "OTHER")
    ) or 0

    return {
        "total_exceptions": total_exceptions,
        "open_exceptions": open_exceptions,
        "resolved_exceptions": resolved_exceptions,
        "damaged": damaged,
        "lost": lost,
        "address_issue": address_issue,
        "customer_unavailable": customer_unavailable,
        "weather_delay": weather_delay,
        "other": other,
    }