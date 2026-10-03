from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.warehouse import Warehouse
from app.schemas.warehouse import WarehouseCreate, WarehouseUpdate


def create_warehouse(
    db: Session,
    warehouse_data: WarehouseCreate,
) -> Warehouse:
    existing_warehouse = db.execute(
        select(Warehouse).where(
            or_(
                Warehouse.name == warehouse_data.name,
                Warehouse.code == warehouse_data.code,
            )
        )
    ).scalar_one_or_none()

    if existing_warehouse is not None:
        if existing_warehouse.name == warehouse_data.name:
            raise ValueError("Warehouse name already exists")

        raise ValueError("Warehouse code already exists")

    warehouse = Warehouse(
        name=warehouse_data.name,
        code=warehouse_data.code,
        address_line1=warehouse_data.address_line1,
        address_line2=warehouse_data.address_line2,
        city=warehouse_data.city,
        state=warehouse_data.state,
        postal_code=warehouse_data.postal_code,
        country=warehouse_data.country,
        contact_phone=warehouse_data.contact_phone,
        contact_email=warehouse_data.contact_email,
        is_active=warehouse_data.is_active,
        description=warehouse_data.description,
    )

    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)

    return warehouse


def get_warehouse_by_id(
    db: Session,
    warehouse_id: int,
) -> Warehouse | None:
    return db.execute(
        select(Warehouse).where(Warehouse.id == warehouse_id)
    ).scalar_one_or_none()


def get_warehouses(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Warehouse]:
    result = db.execute(
        select(Warehouse)
        .order_by(Warehouse.id.desc())
        .offset(skip)
        .limit(limit)
    )

    return list(result.scalars().all())


def update_warehouse(
    db: Session,
    warehouse_id: int,
    warehouse_data: WarehouseUpdate,
) -> Warehouse | None:
    warehouse = get_warehouse_by_id(
        db=db,
        warehouse_id=warehouse_id,
    )

    if warehouse is None:
        return None

    update_data = warehouse_data.model_dump(
        exclude_unset=True,
    )

    new_name = update_data.get("name")
    new_code = update_data.get("code")

    if new_name is not None and new_name != warehouse.name:
        existing_name = db.execute(
            select(Warehouse).where(
                Warehouse.name == new_name,
                Warehouse.id != warehouse_id,
            )
        ).scalar_one_or_none()

        if existing_name is not None:
            raise ValueError("Warehouse name already exists")

    if new_code is not None and new_code != warehouse.code:
        existing_code = db.execute(
            select(Warehouse).where(
                Warehouse.code == new_code,
                Warehouse.id != warehouse_id,
            )
        ).scalar_one_or_none()

        if existing_code is not None:
            raise ValueError("Warehouse code already exists")

    for field, value in update_data.items():
        setattr(warehouse, field, value)

    db.commit()
    db.refresh(warehouse)

    return warehouse