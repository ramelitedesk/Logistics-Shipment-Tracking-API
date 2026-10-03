from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.shipment import Shipment
from app.models.tracking_event import TrackingEvent
from app.schemas.tracking_event import TrackingEventCreate


def create_tracking_event(
    db: Session,
    event_data: TrackingEventCreate,
    created_by: int | None = None,
) -> TrackingEvent:
    shipment = db.execute(
        select(Shipment).where(
            Shipment.id == event_data.shipment_id
        )
    ).scalar_one_or_none()

    if shipment is None:
        raise ValueError("Shipment not found")

    tracking_event = TrackingEvent(
        shipment_id=event_data.shipment_id,
        status=event_data.status.value,
        location=event_data.location,
        facility=event_data.facility,
        description=event_data.description,
        event_time=event_data.event_time,
        created_by=created_by,
        source=event_data.source,
    )

    db.add(tracking_event)
    db.commit()
    db.refresh(tracking_event)

    return tracking_event


def get_tracking_event_by_id(
    db: Session,
    event_id: int,
) -> TrackingEvent | None:
    return db.execute(
        select(TrackingEvent).where(
            TrackingEvent.id == event_id
        )
    ).scalar_one_or_none()


def get_tracking_events_by_shipment(
    db: Session,
    shipment_id: int,
) -> list[TrackingEvent]:
    result = db.execute(
        select(TrackingEvent)
        .where(
            TrackingEvent.shipment_id == shipment_id
        )
        .order_by(
            TrackingEvent.event_time.asc(),
            TrackingEvent.id.asc(),
        )
    )

    return list(result.scalars().all())