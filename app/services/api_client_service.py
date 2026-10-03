import secrets
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.api_client import APIClient
from app.models.user import User
from app.schemas.api_client import APIClientCreate, APIClientUpdate


def generate_client_key() -> str:
    """Generate a unique API client key."""
    return f"lk_{secrets.token_urlsafe(24)}"


def generate_client_secret() -> str:
    """Generate a secure API client secret."""
    return secrets.token_urlsafe(48)


def create_api_client(
    db: Session,
    client_data: APIClientCreate,
) -> tuple[APIClient, str]:
    """
    Create an API client and return:
    - APIClient database object
    - Plaintext client secret

    The plaintext secret is returned only during creation.
    Only its hash is stored in the database.
    """

    # Validate associated user
    user = db.get(User, client_data.user_id)

    if not user:
        raise ValueError("User not found.")

    # Prevent duplicate API client names
    existing_name = db.scalar(
        select(APIClient).where(
            APIClient.name == client_data.name
        )
    )

    if existing_name:
        raise ValueError("API client name already exists.")

    # Generate credentials
    client_key = generate_client_key()
    client_secret = generate_client_secret()

    # Store only the hashed secret
    api_client = APIClient(
        name=client_data.name,
        client_key=client_key,
        client_secret_hash=hash_password(client_secret),
        user_id=client_data.user_id,
        is_active=True,
    )

    db.add(api_client)
    db.commit()
    db.refresh(api_client)

    return api_client, client_secret


def get_api_client(
    db: Session,
    client_id: int,
) -> APIClient | None:
    """Get an API client by ID."""
    return db.get(APIClient, client_id)


def get_api_clients(
    db: Session,
) -> list[APIClient]:
    """Get all API clients."""
    return list(
        db.scalars(
            select(APIClient).order_by(APIClient.id.desc())
        ).all()
    )


def update_api_client(
    db: Session,
    client_id: int,
    client_data: APIClientUpdate,
) -> APIClient:
    """Update API client details."""

    api_client = db.get(APIClient, client_id)

    if not api_client:
        raise ValueError("API client not found.")

    # Update name
    if client_data.name is not None:
        existing_name = db.scalar(
            select(APIClient).where(
                APIClient.name == client_data.name,
                APIClient.id != client_id,
            )
        )

        if existing_name:
            raise ValueError(
                "API client name already exists."
            )

        api_client.name = client_data.name

    # Update active status
    if client_data.is_active is not None:
        api_client.is_active = client_data.is_active

    api_client.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(api_client)

    return api_client


def authenticate_api_client(
    db: Session,
    client_key: str,
    client_secret: str,
) -> APIClient | None:
    """
    Authenticate an API client using client key and secret.

    Returns the APIClient if credentials are valid.
    Returns None if credentials are invalid or client is inactive.
    """

    api_client = db.scalar(
        select(APIClient).where(
            APIClient.client_key == client_key
        )
    )

    if not api_client:
        return None

    if not api_client.is_active:
        return None

    if not verify_password(
        client_secret,
        api_client.client_secret_hash,
    ):
        return None

    # Update last-used timestamp
    api_client.last_used_at = datetime.utcnow()

    db.commit()
    db.refresh(api_client)

    return api_client

def authenticate_api_client_and_create_token(
    db: Session,
    client_key: str,
    client_secret: str,
) -> str | None:
    """
    Authenticate an API client and create a JWT access token.

    Returns None when credentials are invalid or the
    API client is inactive.
    """

    api_client = authenticate_api_client(
        db,
        client_key,
        client_secret,
    )

    if not api_client:
        return None

    token_data = {
        "sub": f"api_client:{api_client.id}",
        "client_id": api_client.id,
        "user_id": api_client.user_id,
        "client_key": api_client.client_key,
        "role": "API_CLIENT",
    }

    return create_access_token(token_data)