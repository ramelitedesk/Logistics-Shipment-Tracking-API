from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user, require_role
from app.core.database import get_db
from app.core.roles import UserRole
from app.models.user import User
from app.schemas.audit_log import AuditLogCreate, AuditLogResponse
from app.services.audit_log_service import (
    create_audit_log,
    get_audit_log,
    get_audit_logs,
    get_audit_logs_by_entity,
    get_audit_logs_by_user,
)


router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"],
)


@router.post(
    "/",
    response_model=AuditLogResponse,
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
def create_audit_log_endpoint(
    audit_data: AuditLogCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_audit_log(db, audit_data)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "/",
    response_model=list[AuditLogResponse],
    dependencies=[
        Depends(
            require_role(
                UserRole.SUPER_ADMIN,
                UserRole.OPERATIONS_MANAGER,
            )
        )
    ],
)
def list_audit_logs(
    db: Session = Depends(get_db),
):
    return get_audit_logs(db)


@router.get(
    "/user/{user_id}",
    response_model=list[AuditLogResponse],
    dependencies=[
        Depends(
            require_role(
                UserRole.SUPER_ADMIN,
                UserRole.OPERATIONS_MANAGER,
            )
        )
    ],
)
def list_audit_logs_by_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    return get_audit_logs_by_user(db, user_id)


@router.get(
    "/entity/{entity_type}/{entity_id}",
    response_model=list[AuditLogResponse],
    dependencies=[
        Depends(
            require_role(
                UserRole.SUPER_ADMIN,
                UserRole.OPERATIONS_MANAGER,
            )
        )
    ],
)
def list_audit_logs_by_entity(
    entity_type: str,
    entity_id: int,
    db: Session = Depends(get_db),
):
    return get_audit_logs_by_entity(
        db,
        entity_type,
        entity_id,
    )


@router.get(
    "/{audit_log_id}",
    response_model=AuditLogResponse,
    dependencies=[
        Depends(
            require_role(
                UserRole.SUPER_ADMIN,
                UserRole.OPERATIONS_MANAGER,
            )
        )
    ],
)
def get_audit_log_by_id(
    audit_log_id: int,
    db: Session = Depends(get_db),
):
    audit_log = get_audit_log(db, audit_log_id)

    if not audit_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found.",
        )

    return audit_log