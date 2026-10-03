from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user, require_role
from app.core.database import get_db
from app.core.roles import UserRole
from app.schemas.delivery_agent import (
    DeliveryAgentCreate,
    DeliveryAgentResponse,
    DeliveryAgentUpdate,
)
from app.services.delivery_agent_service import (
    create_delivery_agent,
    get_delivery_agent,
    get_delivery_agent_by_user,
    get_delivery_agents,
    update_delivery_agent,
)

router = APIRouter(
    prefix="/delivery-agents",
    tags=["Delivery Agents"],
)


@router.post(
    "/",
    response_model=DeliveryAgentResponse,
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
def create_agent(
    agent_data: DeliveryAgentCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_delivery_agent(
            db=db,
            agent_data=agent_data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "/",
    response_model=list[DeliveryAgentResponse],
    dependencies=[
        Depends(
            require_role(
                UserRole.SUPER_ADMIN,
                UserRole.OPERATIONS_MANAGER,
            )
        )
    ],
)
def list_agents(
    db: Session = Depends(get_db),
):
    return get_delivery_agents(db)


@router.get(
    "/me",
    response_model=DeliveryAgentResponse,
)
def get_my_agent_profile(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    agent = get_delivery_agent_by_user(
        db=db,
        user_id=current_user.id,
    )

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery agent profile not found.",
        )

    return agent


@router.get(
    "/{agent_id}",
    response_model=DeliveryAgentResponse,
    dependencies=[
        Depends(
            require_role(
                UserRole.SUPER_ADMIN,
                UserRole.OPERATIONS_MANAGER,
            )
        )
    ],
)
def get_agent(
    agent_id: int,
    db: Session = Depends(get_db),
):
    agent = get_delivery_agent(
        db=db,
        agent_id=agent_id,
    )

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery agent not found.",
        )

    return agent


@router.patch(
    "/{agent_id}",
    response_model=DeliveryAgentResponse,
    dependencies=[
        Depends(
            require_role(
                UserRole.SUPER_ADMIN,
            )
        )
    ],
)
def update_agent(
    agent_id: int,
    agent_data: DeliveryAgentUpdate,
    db: Session = Depends(get_db),
):
    agent = update_delivery_agent(
        db=db,
        agent_id=agent_id,
        agent_data=agent_data,
    )

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery agent not found.",
        )

    return agent