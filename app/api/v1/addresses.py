from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user, require_role
from app.core.database import get_db
from app.core.roles import UserRole
from app.models.user import User
from app.schemas.address import (
    AddressCreate,
    AddressResponse,
    AddressUpdate,
)
from app.services.address_service import (
    create_address,
    get_address_by_id,
    get_addresses_by_customer,
    update_address,
)

router = APIRouter(
    prefix="/addresses",
    tags=["Addresses"],
)


@router.post(
    "/",
    response_model=AddressResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_address(
    address_data: AddressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.SUPER_ADMIN,
            UserRole.OPERATIONS_MANAGER,
        )
    ),
):
    return create_address(
        db=db,
        address_data=address_data,
    )


@router.get(
    "/customer/{customer_id}",
    response_model=list[AddressResponse],
)
def list_customer_addresses(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.SUPER_ADMIN,
            UserRole.OPERATIONS_MANAGER,
        )
    ),
):
    return get_addresses_by_customer(
        db=db,
        customer_id=customer_id,
    )


@router.get(
    "/{address_id}",
    response_model=AddressResponse,
)
def get_single_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.SUPER_ADMIN,
            UserRole.OPERATIONS_MANAGER,
        )
    ),
):
    address = get_address_by_id(
        db=db,
        address_id=address_id,
    )

    if address is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found",
        )

    return address


@router.patch(
    "/{address_id}",
    response_model=AddressResponse,
)
def update_existing_address(
    address_id: int,
    address_data: AddressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.SUPER_ADMIN)
    ),
):
    address = get_address_by_id(
        db=db,
        address_id=address_id,
    )

    if address is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found",
        )

    return update_address(
        db=db,
        address=address,
        address_data=address_data,
    )