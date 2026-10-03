from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate


def create_customer(
    db: Session,
    customer_data: CustomerCreate,
) -> Customer:
    existing_customer = db.execute(
        select(Customer).where(
            Customer.user_id == customer_data.user_id
        )
    ).scalar_one_or_none()

    if existing_customer:
        raise ValueError(
            "Customer profile already exists for this user"
        )

    customer = Customer(
        user_id=customer_data.user_id,
        phone=customer_data.phone,
        company_name=customer_data.company_name,
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return customer


def get_customer_by_id(
    db: Session,
    customer_id: int,
) -> Customer | None:
    return db.execute(
        select(Customer).where(
            Customer.id == customer_id
        )
    ).scalar_one_or_none()


def get_customer_by_user_id(
    db: Session,
    user_id: int,
) -> Customer | None:
    return db.execute(
        select(Customer).where(
            Customer.user_id == user_id
        )
    ).scalar_one_or_none()


def get_customers(
    db: Session,
) -> list[Customer]:
    return list(
        db.execute(
            select(Customer).order_by(Customer.id)
        ).scalars().all()
    )


def update_customer(
    db: Session,
    customer: Customer,
    customer_data: CustomerUpdate,
) -> Customer:
    if customer_data.phone is not None:
        customer.phone = customer_data.phone

    if customer_data.company_name is not None:
        customer.company_name = customer_data.company_name

    db.commit()
    db.refresh(customer)

    return customer