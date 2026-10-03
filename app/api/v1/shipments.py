from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies import require_role
from app.core.database import get_db
from app.core.roles import UserRole
from app.models.user import User
from app.schemas.shipment import (
    ShipmentCreate,
    ShipmentResponse,
    ShipmentUpdate,
)
from app.services.shipment_service import (
    create_shipment,
    get_shipment_by_id,
    get_shipments,
    get_shipments_by_order,
    update_shipment,
)


router = APIRouter(
    prefix="/shipments",
    tags=["Shipments"],
)


@router.post(
    "/",
    response_model=ShipmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_shipment(
    shipment_data: ShipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.SUPER_ADMIN,
            UserRole.OPERATIONS_MANAGER,
        )
    ),
):
    try:
        return create_shipment(
            db=db,
            shipment_data=shipment_data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "/",
    response_model=list[ShipmentResponse],
)
def list_shipments(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.SUPER_ADMIN,
            UserRole.OPERATIONS_MANAGER,
        )
    ),
):
    return get_shipments(db)


@router.get(
    "/order/{order_id}",
    response_model=list[ShipmentResponse],
)
def list_order_shipments(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.SUPER_ADMIN,
            UserRole.OPERATIONS_MANAGER,
        )
    ),
):
    return get_shipments_by_order(
        db=db,
        order_id=order_id,
    )


@router.get(
    "/{shipment_id}",
    response_model=ShipmentResponse,
)
def get_single_shipment(
    shipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.SUPER_ADMIN,
            UserRole.OPERATIONS_MANAGER,
        )
    ),
):
    shipment = get_shipment_by_id(
        db=db,
        shipment_id=shipment_id,
    )

    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found",
        )

    return shipment


@router.patch(
    "/{shipment_id}",
    response_model=ShipmentResponse,
)
def update_shipment_endpoint(
    shipment_id: int,
    shipment_data: ShipmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.SUPER_ADMIN)
    ),
):
    shipment = get_shipment_by_id(
        db=db,
        shipment_id=shipment_id,
    )

    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found",
        )

    try:
        return update_shipment(
            db=db,
            shipment_id=shipment_id,
            shipment_data=shipment_data,
            updated_by=current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )