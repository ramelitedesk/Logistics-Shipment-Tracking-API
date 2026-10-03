from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user, require_role
from app.core.database import get_db
from app.core.roles import UserRole
from app.models.user import User
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationUpdate,
)
from app.services.notification_service import (
    create_notification,
    get_notification,
    get_notifications,
    get_notifications_by_shipment,
    get_notifications_by_user,
    mark_notification_as_read,
    update_notification,
)
from app.services.notification_dispatch_service import dispatch_notification

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.post(
    "/",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_notification_api(
    notification_data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.SUPER_ADMIN,
            UserRole.OPERATIONS_MANAGER,
        )
    ),
):
    try:
        return create_notification(
            db=db,
            notification_data=notification_data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "/",
    response_model=list[NotificationResponse],
)
def list_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.SUPER_ADMIN,
            UserRole.OPERATIONS_MANAGER,
        )
    ),
):
    return get_notifications(db=db)


@router.get(
    "/me",
    response_model=list[NotificationResponse],
)
def list_my_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_notifications_by_user(
        db=db,
        user_id=current_user.id,
    )


@router.get(
    "/user/{user_id}",
    response_model=list[NotificationResponse],
)
def list_user_notifications(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.SUPER_ADMIN,
            UserRole.OPERATIONS_MANAGER,
        )
    ),
):
    return get_notifications_by_user(
        db=db,
        user_id=user_id,
    )


@router.get(
    "/shipment/{shipment_id}",
    response_model=list[NotificationResponse],
)
def list_shipment_notifications(
    shipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_notifications_by_shipment(
        db=db,
        shipment_id=shipment_id,
    )

@router.post(
    "/{notification_id}/dispatch",
)
def dispatch_notification_task(
    notification_id: int,
    current_user=Depends(
        require_role(
            UserRole.SUPER_ADMIN,
            UserRole.OPERATIONS_MANAGER,
        )
    ),
):
    try:
        result = dispatch_notification(
            notification_id
        )

        return {
            "message": "Notification dispatched to background worker.",
            "notification_id": notification_id,
            "task_id": result.id,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )
    
@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
)
def get_notification_api(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notification = get_notification(
        db=db,
        notification_id=notification_id,
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found.",
        )

    return notification


@router.patch(
    "/{notification_id}",
    response_model=NotificationResponse,
)
def update_notification_api(
    notification_id: int,
    notification_data: NotificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.SUPER_ADMIN,
            UserRole.OPERATIONS_MANAGER,
        )
    ),
):
    notification = update_notification(
        db=db,
        notification_id=notification_id,
        notification_data=notification_data,
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found.",
        )

    return notification


@router.post(
    "/{notification_id}/read",
    response_model=NotificationResponse,
)
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notification = get_notification(
        db=db,
        notification_id=notification_id,
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found.",
        )

    if (
        notification.user_id != current_user.id
        and current_user.role
        not in {
            UserRole.SUPER_ADMIN.value,
            UserRole.OPERATIONS_MANAGER.value,
        }
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot modify this notification.",
        )

    return mark_notification_as_read(
        db=db,
        notification_id=notification_id,
    )