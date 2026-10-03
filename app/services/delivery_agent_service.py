from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.delivery_agent import DeliveryAgent
from app.models.user import User
from app.schemas.delivery_agent import (
    DeliveryAgentCreate,
    DeliveryAgentUpdate,
)


def create_delivery_agent(
    db: Session,
    agent_data: DeliveryAgentCreate,
) -> DeliveryAgent:
    # Verify user exists
    user = db.get(User, agent_data.user_id)

    if not user:
        raise ValueError("User not found.")

    # Prevent duplicate delivery-agent profile
    existing_user_agent = db.scalar(
        select(DeliveryAgent).where(
            DeliveryAgent.user_id == agent_data.user_id
        )
    )

    if existing_user_agent:
        raise ValueError(
            "Delivery agent profile already exists for this user."
        )

    # Prevent duplicate employee code
    existing_employee = db.scalar(
        select(DeliveryAgent).where(
            DeliveryAgent.employee_code == agent_data.employee_code
        )
    )

    if existing_employee:
        raise ValueError(
            "Employee code already exists."
        )

    agent = DeliveryAgent(
        user_id=agent_data.user_id,
        employee_code=agent_data.employee_code,
        phone=agent_data.phone,
        vehicle_type=agent_data.vehicle_type,
        vehicle_number=agent_data.vehicle_number,
        license_number=agent_data.license_number,
        is_available=agent_data.is_available,
        is_active=agent_data.is_active,
        notes=agent_data.notes,
    )

    db.add(agent)
    db.commit()
    db.refresh(agent)

    return agent


def get_delivery_agent(
    db: Session,
    agent_id: int,
) -> DeliveryAgent | None:
    return db.get(DeliveryAgent, agent_id)


def get_delivery_agent_by_user(
    db: Session,
    user_id: int,
) -> DeliveryAgent | None:
    return db.scalar(
        select(DeliveryAgent).where(
            DeliveryAgent.user_id == user_id
        )
    )


def get_delivery_agents(
    db: Session,
) -> list[DeliveryAgent]:
    return list(
        db.scalars(
            select(DeliveryAgent).order_by(
                DeliveryAgent.id.desc()
            )
        ).all()
    )


def update_delivery_agent(
    db: Session,
    agent_id: int,
    agent_data: DeliveryAgentUpdate,
) -> DeliveryAgent | None:
    agent = db.get(DeliveryAgent, agent_id)

    if not agent:
        return None

    update_data = agent_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(agent, field, value)

    db.commit()
    db.refresh(agent)

    return agent