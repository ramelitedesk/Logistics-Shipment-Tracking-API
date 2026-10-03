from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ProofOfDelivery(Base):
    __tablename__ = "proof_of_deliveries"

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

    delivery_attempt_id: Mapped[int] = mapped_column(
        ForeignKey("delivery_attempts.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    recipient_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    signature_reference: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    photo_reference: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    delivered_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    shipment = relationship(
        "Shipment",
        backref="proof_of_delivery",
    )

    delivery_attempt = relationship(
        "DeliveryAttempt",
        backref="proof_of_delivery",
    )