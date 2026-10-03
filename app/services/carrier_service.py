from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.carrier import Carrier
from app.schemas.carrier import CarrierCreate, CarrierUpdate


def create_carrier(
    db: Session,
    carrier_data: CarrierCreate,
) -> Carrier:
    existing_name = db.execute(
        select(Carrier).where(
            Carrier.name == carrier_data.name
        )
    ).scalar_one_or_none()

    if existing_name:
        raise ValueError(
            "Carrier with this name already exists"
        )

    existing_code = db.execute(
        select(Carrier).where(
            Carrier.code == carrier_data.code
        )
    ).scalar_one_or_none()

    if existing_code:
        raise ValueError(
            "Carrier with this code already exists"
        )

    carrier = Carrier(
        name=carrier_data.name,
        code=carrier_data.code,
        contact_email=carrier_data.contact_email,
        contact_phone=carrier_data.contact_phone,
        api_base_url=carrier_data.api_base_url,
        is_active=carrier_data.is_active,
        description=carrier_data.description,
    )

    db.add(carrier)
    db.commit()
    db.refresh(carrier)

    return carrier


def get_carrier_by_id(
    db: Session,
    carrier_id: int,
) -> Carrier | None:
    return db.execute(
        select(Carrier).where(
            Carrier.id == carrier_id
        )
    ).scalar_one_or_none()


def get_carriers(
    db: Session,
) -> list[Carrier]:
    result = db.execute(
        select(Carrier).order_by(
            Carrier.id.asc()
        )
    )

    return list(result.scalars().all())


def update_carrier(
    db: Session,
    carrier: Carrier,
    carrier_data: CarrierUpdate,
) -> Carrier:
    if carrier_data.name is not None:
        existing_name = db.execute(
            select(Carrier).where(
                Carrier.name == carrier_data.name,
                Carrier.id != carrier.id,
            )
        ).scalar_one_or_none()

        if existing_name:
            raise ValueError(
                "Carrier with this name already exists"
            )

        carrier.name = carrier_data.name

    if carrier_data.code is not None:
        existing_code = db.execute(
            select(Carrier).where(
                Carrier.code == carrier_data.code,
                Carrier.id != carrier.id,
            )
        ).scalar_one_or_none()

        if existing_code:
            raise ValueError(
                "Carrier with this code already exists"
            )

        carrier.code = carrier_data.code

    if carrier_data.contact_email is not None:
        carrier.contact_email = carrier_data.contact_email

    if carrier_data.contact_phone is not None:
        carrier.contact_phone = carrier_data.contact_phone

    if carrier_data.api_base_url is not None:
        carrier.api_base_url = carrier_data.api_base_url

    if carrier_data.is_active is not None:
        carrier.is_active = carrier_data.is_active

    if carrier_data.description is not None:
        carrier.description = carrier_data.description

    db.commit()
    db.refresh(carrier)

    return carrier