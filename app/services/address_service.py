from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.address import Address
from app.schemas.address import AddressCreate, AddressUpdate


def create_address(
    db: Session,
    address_data: AddressCreate,
) -> Address:
    if address_data.is_default:
        existing_default = db.execute(
            select(Address).where(
                Address.customer_id == address_data.customer_id,
                Address.is_default.is_(True),
            )
        ).scalars().all()

        for address in existing_default:
            address.is_default = False

    address = Address(
        customer_id=address_data.customer_id,
        address_type=address_data.address_type,
        address_line1=address_data.address_line1,
        address_line2=address_data.address_line2,
        city=address_data.city,
        state=address_data.state,
        postal_code=address_data.postal_code,
        country=address_data.country,
        is_default=address_data.is_default,
    )

    db.add(address)
    db.commit()
    db.refresh(address)

    return address


def get_address_by_id(
    db: Session,
    address_id: int,
) -> Address | None:
    return db.execute(
        select(Address).where(
            Address.id == address_id
        )
    ).scalar_one_or_none()


def get_addresses_by_customer(
    db: Session,
    customer_id: int,
) -> list[Address]:
    return list(
        db.execute(
            select(Address)
            .where(Address.customer_id == customer_id)
            .order_by(Address.id)
        ).scalars().all()
    )


def update_address(
    db: Session,
    address: Address,
    address_data: AddressUpdate,
) -> Address:
    if address_data.is_default is True:
        existing_default = db.execute(
            select(Address).where(
                Address.customer_id == address.customer_id,
                Address.is_default.is_(True),
                Address.id != address.id,
            )
        ).scalars().all()

        for existing_address in existing_default:
            existing_address.is_default = False

    if address_data.address_type is not None:
        address.address_type = address_data.address_type

    if address_data.address_line1 is not None:
        address.address_line1 = address_data.address_line1

    if address_data.address_line2 is not None:
        address.address_line2 = address_data.address_line2

    if address_data.city is not None:
        address.city = address_data.city

    if address_data.state is not None:
        address.state = address_data.state

    if address_data.postal_code is not None:
        address.postal_code = address_data.postal_code

    if address_data.country is not None:
        address.country = address_data.country

    if address_data.is_default is not None:
        address.is_default = address_data.is_default

    db.commit()
    db.refresh(address)

    return address