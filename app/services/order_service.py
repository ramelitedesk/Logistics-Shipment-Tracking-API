from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.order_item import OrderItem
from app.schemas.order import OrderCreate, OrderUpdate
from app.core.order_status import OrderStatus

def create_order(
    db: Session,
    order_data: OrderCreate,
) -> Order:
    existing_order = db.execute(
        select(Order).where(
            Order.order_number == order_data.order_number
        )
    ).scalar_one_or_none()

    if existing_order:
        raise ValueError(
            "Order with this order number already exists"
        )

    order = Order(
        customer_id=order_data.customer_id,
        order_number=order_data.order_number,
        status="PENDING",
        notes=order_data.notes,
    )

    for item_data in order_data.items:
        item = OrderItem(
            product_name=item_data.product_name,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
        )
        order.items.append(item)

    db.add(order)
    db.commit()
    db.refresh(order)

    return order


def get_order_by_id(
    db: Session,
    order_id: int,
) -> Order | None:
    return db.execute(
        select(Order).where(
            Order.id == order_id
        )
    ).scalar_one_or_none()


def get_orders(
    db: Session,
) -> list[Order]:
    return list(
        db.execute(
            select(Order).order_by(Order.id)
        ).scalars().unique().all()
    )


def get_orders_by_customer(
    db: Session,
    customer_id: int,
) -> list[Order]:
    return list(
        db.execute(
            select(Order)
            .where(Order.customer_id == customer_id)
            .order_by(Order.id)
        ).scalars().unique().all()
    )


def update_order(
    db: Session,
    order: Order,
    order_data: OrderUpdate,
) -> Order:
    if order_data.status is not None:
        order.status = order_data.status

    if order_data.notes is not None:
        order.notes = order_data.notes

    db.commit()
    db.refresh(order)

    return order


ALLOWED_ORDER_TRANSITIONS = {
    OrderStatus.PENDING: {
        OrderStatus.CONFIRMED,
        OrderStatus.CANCELLED,
    },
    OrderStatus.CONFIRMED: {
        OrderStatus.PROCESSING,
        OrderStatus.CANCELLED,
    },
    OrderStatus.PROCESSING: {
        OrderStatus.READY_FOR_SHIPMENT,
        OrderStatus.CANCELLED,
    },
    OrderStatus.READY_FOR_SHIPMENT: {
        OrderStatus.COMPLETED,
    },
    OrderStatus.COMPLETED: set(),
    OrderStatus.CANCELLED: set(),
}


def update_order(db: Session, order: Order, order_data: OrderUpdate) -> Order:
    if order_data.status is not None:
        current_status = OrderStatus(order.status)
        new_status = order_data.status

        if new_status != current_status:
            allowed_statuses = ALLOWED_ORDER_TRANSITIONS.get(
                current_status,
                set(),
            )

            if new_status not in allowed_statuses:
                raise ValueError(
                    f"Invalid order status transition: "
                    f"{current_status.value} -> {new_status.value}"
                )

            order.status = new_status.value

    if order_data.notes is not None:
        order.notes = order_data.notes

    db.commit()
    db.refresh(order)

    return order