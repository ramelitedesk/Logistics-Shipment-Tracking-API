from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ShipmentAssignment(Base):
    __tablename__ = "shipment_assignments"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    shipment_id: Mapped[int] = mapped_column(
        ForeignKey("shipments.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    delivery_agent_id: Mapped[int] = mapped_column(
        ForeignKey("delivery_agents.id"),
        nullable=False,
        index=True,
    )

    assigned_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    shipment = relationship(
        "Shipment",
        backref="assignment",
    )

    delivery_agent = relationship(
        "DeliveryAgent",
        backref="shipment_assignments",
    )