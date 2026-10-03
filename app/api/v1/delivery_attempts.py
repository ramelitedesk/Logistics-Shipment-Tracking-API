from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user, require_role
from app.core.database import get_db
from app.core.roles import UserRole
from app.models.user import User
from app.schemas.delivery_attempt import (
    DeliveryAttemptCreate,
    DeliveryAttemptResponse,
    DeliveryAttemptUpdate,
)
from app.services.delivery_attempt_service import (
    create_delivery_attempt,
    get_attempts_by_shipment,
    get_delivery_attempt,
    get_delivery_attempts,
    update_delivery_attempt,
)


router = APIRouter(
    prefix="/delivery-attempts",
    tags=["Delivery Attempts"],
)


@router.post(
    "/",
    response_model=DeliveryAttemptResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_attempt(
    attempt_data: DeliveryAttemptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.SUPER_ADMIN,
            UserRole.OPERATIONS_MANAGER,
            UserRole.DELIVERY_AGENT,
        )
    ),
):
    try:
        return create_delivery_attempt(
            db=db,
            attempt_data=attempt_data,
            created_by=current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "/",
    response_model=list[DeliveryAttemptResponse],
)
def list_attempts(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.SUPER_ADMIN,
            UserRole.OPERATIONS_MANAGER,
        )
    ),
):
    return get_delivery_attempts(db=db)


@router.get(
    "/shipment/{shipment_id}",
    response_model=list[DeliveryAttemptResponse],
)
def list_shipment_attempts(
    shipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_attempts_by_shipment(
        db=db,
        shipment_id=shipment_id,
    )


@router.get(
    "/{attempt_id}",
    response_model=DeliveryAttemptResponse,
)
def get_attempt(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attempt = get_delivery_attempt(
        db=db,
        attempt_id=attempt_id,
    )

    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery attempt not found.",
        )

    return attempt


@router.patch(
    "/{attempt_id}",
    response_model=DeliveryAttemptResponse,
)
def update_attempt(
    attempt_id: int,
    attempt_data: DeliveryAttemptUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.SUPER_ADMIN,
            UserRole.OPERATIONS_MANAGER,
            UserRole.DELIVERY_AGENT,
        )
    ),
):
    try:
        attempt = update_delivery_attempt(
            db=db,
            attempt_id=attempt_id,
            attempt_data=attempt_data,
            updated_by=current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery attempt not found.",
        )

    return attempt