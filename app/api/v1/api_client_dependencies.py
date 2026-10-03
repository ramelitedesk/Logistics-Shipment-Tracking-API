from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.api_client import APIClient


api_client_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/api-clients/authenticate"
)


def get_current_api_client(
    token: str = Depends(api_client_oauth2_scheme),
    db: Session = Depends(get_db),
) -> APIClient:

    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API client token.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    subject = payload.get("sub")

    if not subject or not subject.startswith("api_client:"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API client token.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    try:
        client_id = int(
            subject.split(":", 1)[1]
        )
    except (ValueError, IndexError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API client token.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    api_client = db.get(
        APIClient,
        client_id,
    )

    if not api_client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API client not found.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    if not api_client.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API client is inactive.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    return api_client