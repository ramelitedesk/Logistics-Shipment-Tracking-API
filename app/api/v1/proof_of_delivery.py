from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user, require_role
from app.core.database import get_db
from app.core.roles import UserRole
from app.models.user import User
from app.schemas.proof_of_delivery import (
    ProofOfDeliveryCreate,
    ProofOfDeliveryResponse,
    ProofOfDeliveryUpdate,
)
from app.services.proof_of_delivery_service import (
    create_proof_of_delivery,
    get_proof_of_deliveries,
    get_proof_of_delivery,
    get_proof_of_delivery_by_shipment,
    update_proof_of_delivery,
)


router = APIRouter(
    prefix="/proof-of-delivery",
    tags=["Proof of Delivery"],
)


# ---------------------------------------------------------
# CREATE PROOF OF DELIVERY
# ---------------------------------------------------------
@router.post(
    "/",
    response_model=ProofOfDeliveryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_pod(
    pod_data: ProofOfDeliveryCreate,
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
        return create_proof_of_delivery(
            db=db,
            pod_data=pod_data,
            created_by=current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


# ---------------------------------------------------------
# LIST ALL PROOF OF DELIVERY RECORDS
# ---------------------------------------------------------
@router.get(
    "/",
    response_model=list[ProofOfDeliveryResponse],
)
def list_pods(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.SUPER_ADMIN,
            UserRole.OPERATIONS_MANAGER,
        )
    ),
):
    return get_proof_of_deliveries(
        db=db,
    )


# ---------------------------------------------------------
# GET PROOF OF DELIVERY BY SHIPMENT
# ---------------------------------------------------------
@router.get(
    "/shipment/{shipment_id}",
    response_model=ProofOfDeliveryResponse,
)
def get_shipment_pod(
    shipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pod = get_proof_of_delivery_by_shipment(
        db=db,
        shipment_id=shipment_id,
    )

    if not pod:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proof of delivery not found.",
        )

    return pod


# ---------------------------------------------------------
# GET PROOF OF DELIVERY BY ID
# ---------------------------------------------------------
@router.get(
    "/{pod_id}",
    response_model=ProofOfDeliveryResponse,
)
def get_pod(
    pod_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pod = get_proof_of_delivery(
        db=db,
        pod_id=pod_id,
    )

    if not pod:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proof of delivery not found.",
        )

    return pod


# ---------------------------------------------------------
# UPDATE PROOF OF DELIVERY
# ---------------------------------------------------------
@router.patch(
    "/{pod_id}",
    response_model=ProofOfDeliveryResponse,
)
def update_pod(
    pod_id: int,
    pod_data: ProofOfDeliveryUpdate,
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
        pod = update_proof_of_delivery(
            db=db,
            pod_id=pod_id,
            pod_data=pod_data,
            updated_by=current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    if not pod:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proof of delivery not found.",
        )

    return pod