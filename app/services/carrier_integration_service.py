from sqlalchemy.orm import Session

from app.integrations.carriers.factory import get_carrier_adapter
from app.models.carrier import Carrier


def get_adapter_for_carrier(
    db: Session,
    carrier_id: int,
):
    carrier = db.get(Carrier, carrier_id)

    if carrier is None:
        raise ValueError("Carrier not found")

    if not carrier.is_active:
        raise ValueError("Carrier is inactive")

    return get_carrier_adapter(carrier.code)


def create_external_shipment(
    db: Session,
    carrier_id: int,
    shipment_data: dict,
) -> dict:
    adapter = get_adapter_for_carrier(
        db=db,
        carrier_id=carrier_id,
    )

    return adapter.create_shipment(shipment_data)


def get_external_tracking(
    db: Session,
    carrier_id: int,
    tracking_number: str,
) -> dict:
    adapter = get_adapter_for_carrier(
        db=db,
        carrier_id=carrier_id,
    )

    return adapter.get_tracking(tracking_number)


def cancel_external_shipment(
    db: Session,
    carrier_id: int,
    tracking_number: str,
) -> dict:
    adapter = get_adapter_for_carrier(
        db=db,
        carrier_id=carrier_id,
    )

    return adapter.cancel_shipment(tracking_number)


def generate_external_label(
    db: Session,
    carrier_id: int,
    tracking_number: str,
) -> dict:
    adapter = get_adapter_for_carrier(
        db=db,
        carrier_id=carrier_id,
    )

    return adapter.generate_label(tracking_number)