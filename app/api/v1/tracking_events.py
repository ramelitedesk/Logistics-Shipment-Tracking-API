from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies import (
    get_current_user,
    require_role,
)
from app.core.database import get_db
from app.core.roles import UserRole
from app.models.user import User
from app.schemas.tracking_event import (
    TrackingEventCreate,
    TrackingEventResponse,
)
from app.services.tracking_event_service import (
    create_tracking_event,
    get_tracking_event_by_id,
    get_tracking_events_by_shipment,
)


router = APIRouter(
    prefix="/tracking-events",
    tags=["Tracking Events"],
)


@router.post(
    "/",
    response_model=TrackingEventResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_tracking_event_endpoint(
    event_data: TrackingEventCreate,
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
        return create_tracking_event(
            db=db,
            event_data=event_data,
            created_by=current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "/shipment/{shipment_id}",
    response_model=list[TrackingEventResponse],
)
def get_shipment_tracking_events(
    shipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_tracking_events_by_shipment(
        db=db,
        shipment_id=shipment_id,
    )


@router.get(
    "/{event_id}",
    response_model=TrackingEventResponse,
)
def get_tracking_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = get_tracking_event_by_id(
        db=db,
        event_id=event_id,
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tracking event not found",
        )

    return event