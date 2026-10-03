from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user, require_role
from app.core.database import get_db
from app.core.roles import UserRole
from app.models.user import User
from app.schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderUpdate,
)
from app.services.order_service import (
    create_order,
    get_order_by_id,
    get_orders,
    get_orders_by_customer,
    update_order,
)

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.SUPER_ADMIN,
            UserRole.OPERATIONS_MANAGER,
        )
    ),
):
    try:
        return create_order(
            db=db,
            order_data=order_data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "/",
    response_model=list[OrderResponse],
)
def list_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.SUPER_ADMIN,
            UserRole.OPERATIONS_MANAGER,
        )
    ),
):
    return get_orders(db)


@router.get(
    "/customer/{customer_id}",
    response_model=list[OrderResponse],
)
def list_customer_orders(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.SUPER_ADMIN,
            UserRole.OPERATIONS_MANAGER,
        )
    ),
):
    return get_orders_by_customer(
        db=db,
        customer_id=customer_id,
    )


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
)
def get_single_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.SUPER_ADMIN,
            UserRole.OPERATIONS_MANAGER,
        )
    ),
):
    order = get_order_by_id(
        db=db,
        order_id=order_id,
    )

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    return order


@router.patch(
    "/{order_id}",
    response_model=OrderResponse,
)
def update_existing_order(
    order_id: int,
    order_data: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.SUPER_ADMIN)
    ),
):
    order = get_order_by_id(
        db=db,
        order_id=order_id,
    )

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    try:
        return update_order(
            db=db,
            order=order,
            order_data=order_data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )