from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user, require_role
from app.core.database import get_db
from app.core.roles import UserRole
from app.models.user import User
from app.schemas.shipment_exception import (
    ShipmentExceptionCreate,
    ShipmentExceptionResponse,
    ShipmentExceptionUpdate,
)
from app.services.shipment_exception_service import (
    create_shipment_exception,
    get_exceptions_by_shipment,
    get_shipment_exception,
    get_shipment_exceptions,
    update_shipment_exception,
)


router = APIRouter(
    prefix="/shipment-exceptions",
    tags=["Shipment Exceptions"],
)


# ---------------------------------------------------------
# CREATE SHIPMENT EXCEPTION
# ---------------------------------------------------------
@router.post(
    "/",
    response_model=ShipmentExceptionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_exception(
    exception_data: ShipmentExceptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.SUPER_ADMIN,
            UserRole.OPERATIONS_MANAGER,
            UserRole.WAREHOUSE_STAFF,
            UserRole.DELIVERY_AGENT,
        )
    ),
):
    try:
        return create_shipment_exception(
            db=db,
            exception_data=exception_data,
            reported_by=current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


# ---------------------------------------------------------
# LIST ALL SHIPMENT EXCEPTIONS
# ---------------------------------------------------------
@router.get(
    "/",
    response_model=list[ShipmentExceptionResponse],
)
def list_exceptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.SUPER_ADMIN,
            UserRole.OPERATIONS_MANAGER,
        )
    ),
):
    return get_shipment_exceptions(
        db=db,
    )


# ---------------------------------------------------------
# LIST EXCEPTIONS BY SHIPMENT
# ---------------------------------------------------------
@router.get(
    "/shipment/{shipment_id}",
    response_model=list[ShipmentExceptionResponse],
)
def list_shipment_exceptions(
    shipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_exceptions_by_shipment(
        db=db,
        shipment_id=shipment_id,
    )


# ---------------------------------------------------------
# GET SHIPMENT EXCEPTION BY ID
# ---------------------------------------------------------
@router.get(
    "/{exception_id}",
    response_model=ShipmentExceptionResponse,
)
def get_exception(
    exception_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    shipment_exception = get_shipment_exception(
        db=db,
        exception_id=exception_id,
    )

    if not shipment_exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment exception not found.",
        )

    return shipment_exception


# ---------------------------------------------------------
# UPDATE SHIPMENT EXCEPTION
# ---------------------------------------------------------
@router.patch(
    "/{exception_id}",
    response_model=ShipmentExceptionResponse,
)
def update_exception(
    exception_id: int,
    exception_data: ShipmentExceptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.SUPER_ADMIN,
            UserRole.OPERATIONS_MANAGER,
        )
    ),
):
    try:
        shipment_exception = update_shipment_exception(
            db=db,
            exception_id=exception_id,
            exception_data=exception_data,
            updated_by=current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    if not shipment_exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment exception not found.",
        )

    return shipment_exception