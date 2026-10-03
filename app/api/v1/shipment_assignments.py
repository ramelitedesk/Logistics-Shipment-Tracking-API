from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user, require_role
from app.core.database import get_db
from app.core.roles import UserRole
from app.models.user import User
from app.schemas.shipment_assignment import (
    ShipmentAssignmentCreate,
    ShipmentAssignmentResponse,
    ShipmentAssignmentUpdate,
)
from app.services.shipment_assignment_service import (
    create_shipment_assignment,
    get_assignment_by_shipment,
    get_assignments,
    get_shipment_assignment,
    update_shipment_assignment,
)


router = APIRouter(
    prefix="/shipment-assignments",
    tags=["Shipment Assignments"],
)


# =========================================================
# CREATE SHIPMENT ASSIGNMENT
# =========================================================

@router.post(
    "/",
    response_model=ShipmentAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            require_role(
                UserRole.SUPER_ADMIN,
                UserRole.OPERATIONS_MANAGER,
            )
        )
    ],
)
def create_assignment(
    assignment_data: ShipmentAssignmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return create_shipment_assignment(
            db=db,
            assignment_data=assignment_data,
            created_by=current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


# =========================================================
# LIST ALL SHIPMENT ASSIGNMENTS
# =========================================================

@router.get(
    "/",
    response_model=list[ShipmentAssignmentResponse],
    dependencies=[
        Depends(
            require_role(
                UserRole.SUPER_ADMIN,
                UserRole.OPERATIONS_MANAGER,
            )
        )
    ],
)
def list_assignments(
    db: Session = Depends(get_db),
):
    return get_assignments(db)


# =========================================================
# GET ASSIGNMENT BY SHIPMENT
# =========================================================

@router.get(
    "/shipment/{shipment_id}",
    response_model=ShipmentAssignmentResponse,
)
def get_assignment_for_shipment(
    shipment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assignment = get_assignment_by_shipment(
        db=db,
        shipment_id=shipment_id,
    )

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment assignment not found.",
        )

    return assignment


# =========================================================
# GET ASSIGNMENT BY ID
# =========================================================

@router.get(
    "/{assignment_id}",
    response_model=ShipmentAssignmentResponse,
    dependencies=[
        Depends(
            require_role(
                UserRole.SUPER_ADMIN,
                UserRole.OPERATIONS_MANAGER,
            )
        )
    ],
)
def get_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
):
    assignment = get_shipment_assignment(
        db=db,
        assignment_id=assignment_id,
    )

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment assignment not found.",
        )

    return assignment


# =========================================================
# UPDATE / REASSIGN SHIPMENT
# =========================================================

@router.patch(
    "/{assignment_id}",
    response_model=ShipmentAssignmentResponse,
    dependencies=[
        Depends(
            require_role(
                UserRole.SUPER_ADMIN,
                UserRole.OPERATIONS_MANAGER,
            )
        )
    ],
)
def update_assignment(
    assignment_id: int,
    assignment_data: ShipmentAssignmentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        assignment = update_shipment_assignment(
            db=db,
            assignment_id=assignment_id,
            assignment_data=assignment_data,
            updated_by=current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment assignment not found.",
        )

    return assignment