from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user, require_role
from app.core.database import get_db
from app.core.roles import UserRole
from app.models.user import User
from app.schemas.webhook import (
    WebhookCreate,
    WebhookResponse,
    WebhookUpdate,
)
from app.services.webhook_service import (
    create_webhook,
    get_webhook,
    get_webhooks,
    get_webhooks_by_carrier,
    get_webhooks_by_shipment,
    process_webhook,
    update_webhook,
)


router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"],
)


# ---------------------------------------------------------
# CREATE WEBHOOK
# ---------------------------------------------------------
@router.post(
    "/",
    response_model=WebhookResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_webhook_api(
    webhook_data: WebhookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.SUPER_ADMIN,
            UserRole.OPERATIONS_MANAGER,
        )
    ),
):
    try:
        return create_webhook(
            db=db,
            webhook_data=webhook_data,
            created_by=current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


# ---------------------------------------------------------
# LIST ALL WEBHOOKS
# ---------------------------------------------------------
@router.get(
    "/",
    response_model=list[WebhookResponse],
)
def list_webhooks(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.SUPER_ADMIN,
            UserRole.OPERATIONS_MANAGER,
        )
    ),
):
    return get_webhooks(
        db=db,
    )


# ---------------------------------------------------------
# LIST WEBHOOKS BY SHIPMENT
# ---------------------------------------------------------
@router.get(
    "/shipment/{shipment_id}",
    response_model=list[WebhookResponse],
)
def list_shipment_webhooks(
    shipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_webhooks_by_shipment(
        db=db,
        shipment_id=shipment_id,
    )


# ---------------------------------------------------------
# LIST WEBHOOKS BY CARRIER
# ---------------------------------------------------------
@router.get(
    "/carrier/{carrier_id}",
    response_model=list[WebhookResponse],
)
def list_carrier_webhooks(
    carrier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.SUPER_ADMIN,
            UserRole.OPERATIONS_MANAGER,
        )
    ),
):
    return get_webhooks_by_carrier(
        db=db,
        carrier_id=carrier_id,
    )


# ---------------------------------------------------------
# PROCESS WEBHOOK
# ---------------------------------------------------------
@router.post(
    "/{webhook_id}/process",
    response_model=WebhookResponse,
)
def process_webhook_api(
    webhook_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.SUPER_ADMIN,
            UserRole.OPERATIONS_MANAGER,
        )
    ),
):
    try:
        return process_webhook(
            db=db,
            webhook_id=webhook_id,
            processed_by=current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


# ---------------------------------------------------------
# GET WEBHOOK BY ID
# ---------------------------------------------------------
@router.get(
    "/{webhook_id}",
    response_model=WebhookResponse,
)
def get_webhook_api(
    webhook_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    webhook = get_webhook(
        db=db,
        webhook_id=webhook_id,
    )

    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found.",
        )

    return webhook


# ---------------------------------------------------------
# UPDATE WEBHOOK
# ---------------------------------------------------------
@router.patch(
    "/{webhook_id}",
    response_model=WebhookResponse,
)
def update_webhook_api(
    webhook_id: int,
    webhook_data: WebhookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.SUPER_ADMIN,
            UserRole.OPERATIONS_MANAGER,
        )
    ),
):
    try:
        webhook = update_webhook(
            db=db,
            webhook_id=webhook_id,
            webhook_data=webhook_data,
            updated_by=current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found.",
        )

    return webhook