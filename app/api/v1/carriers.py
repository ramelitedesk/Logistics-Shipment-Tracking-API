from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies import require_role
from app.core.database import get_db
from app.core.roles import UserRole
from app.models.user import User
from app.schemas.carrier import (
    CarrierCreate,
    CarrierResponse,
    CarrierUpdate,
)
from app.services.carrier_service import (
    create_carrier,
    get_carrier_by_id,
    get_carriers,
    update_carrier,
)

router = APIRouter(
    prefix="/carriers",
    tags=["Carriers"],
)


@router.post(
    "/",
    response_model=CarrierResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_carrier_endpoint(
    carrier_data: CarrierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.SUPER_ADMIN,
            UserRole.OPERATIONS_MANAGER,
        )
    ),
):
    try:
        return create_carrier(
            db=db,
            carrier_data=carrier_data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "/",
    response_model=list[CarrierResponse],
)
def list_carriers(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.SUPER_ADMIN,
            UserRole.OPERATIONS_MANAGER,
        )
    ),
):
    return get_carriers(db=db)


@router.get(
    "/{carrier_id}",
    response_model=CarrierResponse,
)
def get_carrier(
    carrier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.SUPER_ADMIN,
            UserRole.OPERATIONS_MANAGER,
        )
    ),
):
    carrier = get_carrier_by_id(
        db=db,
        carrier_id=carrier_id,
    )

    if carrier is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carrier not found",
        )

    return carrier


@router.patch(
    "/{carrier_id}",
    response_model=CarrierResponse,
)
def update_carrier_endpoint(
    carrier_id: int,
    carrier_data: CarrierUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.SUPER_ADMIN,
        )
    ),
):
    carrier = get_carrier_by_id(
        db=db,
        carrier_id=carrier_id,
    )

    if carrier is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carrier not found",
        )

    try:
        return update_carrier(
            db=db,
            carrier=carrier,
            carrier_data=carrier_data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )