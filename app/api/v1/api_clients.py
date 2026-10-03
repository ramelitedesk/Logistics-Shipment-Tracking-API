from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies import require_role
from app.api.v1.api_client_dependencies import get_current_api_client
from app.api.v1.rate_limit_dependencies import rate_limit_api_client

from app.core.database import get_db
from app.core.roles import UserRole

from app.schemas.api_client import (
    APIClientAuthRequest,
    APIClientCreate,
    APIClientCreateResponse,
    APIClientResponse,
    APIClientTokenResponse,
    APIClientUpdate,
)

from app.services.api_client_service import (
    authenticate_api_client_and_create_token,
    create_api_client,
    get_api_client,
    get_api_clients,
    update_api_client,
)


router = APIRouter(
    prefix="/api-clients",
    tags=["API Clients"],
)


# ============================================================
# Create API Client
# ============================================================

@router.post(
    "/",
    response_model=APIClientCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_client(
    client_data: APIClientCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(UserRole.SUPER_ADMIN)
    ),
):
    try:
        api_client, client_secret = create_api_client(
            db,
            client_data,
        )

        return {
            "id": api_client.id,
            "name": api_client.name,
            "client_key": api_client.client_key,
            "client_secret": client_secret,
            "user_id": api_client.user_id,
            "is_active": api_client.is_active,
            "created_at": api_client.created_at,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


# ============================================================
# List API Clients
# ============================================================

@router.get(
    "/",
    response_model=list[APIClientResponse],
)
def list_clients(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(UserRole.SUPER_ADMIN)
    ),
):
    return get_api_clients(db)


# ============================================================
# Authenticate API Client
# ============================================================

@router.post(
    "/authenticate",
    response_model=APIClientTokenResponse,
)
def authenticate_client(
    auth_data: APIClientAuthRequest,
    db: Session = Depends(get_db),
):
    access_token = authenticate_api_client_and_create_token(
        db,
        auth_data.client_key,
        auth_data.client_secret,
    )

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API client credentials.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# ============================================================
# Get Authenticated API Client
# Protected by Redis Rate Limiting
# ============================================================

@router.get(
    "/me",
    dependencies=[
        Depends(rate_limit_api_client)
    ],
)
def get_authenticated_api_client(
    current_api_client=Depends(
        get_current_api_client
    ),
):
    return {
        "client_id": current_api_client.id,
        "client_name": current_api_client.name,
        "client_key": current_api_client.client_key,
        "user_id": current_api_client.user_id,
        "is_active": current_api_client.is_active,
    }


# ============================================================
# Get API Client
# ============================================================

@router.get(
    "/{client_id}",
    response_model=APIClientResponse,
)
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(UserRole.SUPER_ADMIN)
    ),
):
    api_client = get_api_client(
        db,
        client_id,
    )

    if not api_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API client not found.",
        )

    return api_client


# ============================================================
# Update API Client
# ============================================================

@router.patch(
    "/{client_id}",
    response_model=APIClientResponse,
)
def update_client(
    client_id: int,
    client_data: APIClientUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(UserRole.SUPER_ADMIN)
    ),
):
    try:
        return update_api_client(
            db,
            client_id,
            client_data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )