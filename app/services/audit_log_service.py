from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit_log import AuditLogCreate


def create_audit_log(
    db: Session,
    audit_data: AuditLogCreate,
) -> AuditLog:

    if audit_data.user_id is not None:
        user = db.get(User, audit_data.user_id)

        if not user:
            raise ValueError("User not found.")

    audit_log = AuditLog(
        user_id=audit_data.user_id,
        action=audit_data.action,
        entity_type=audit_data.entity_type,
        entity_id=audit_data.entity_id,
        old_value=audit_data.old_value,
        new_value=audit_data.new_value,
        ip_address=audit_data.ip_address,
    )

    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)

    return audit_log


def get_audit_log(
    db: Session,
    audit_log_id: int,
) -> AuditLog | None:

    return db.get(AuditLog, audit_log_id)


def get_audit_logs(
    db: Session,
) -> list[AuditLog]:

    return list(
        db.scalars(
            select(AuditLog)
            .order_by(AuditLog.id.desc())
        ).all()
    )


def get_audit_logs_by_user(
    db: Session,
    user_id: int,
) -> list[AuditLog]:

    return list(
        db.scalars(
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
            .order_by(AuditLog.id.desc())
        ).all()
    )


def get_audit_logs_by_entity(
    db: Session,
    entity_type: str,
    entity_id: int,
) -> list[AuditLog]:

    return list(
        db.scalars(
            select(AuditLog)
            .where(
                AuditLog.entity_type == entity_type,
                AuditLog.entity_id == entity_id,
            )
            .order_by(AuditLog.id.desc())
        ).all()
    )