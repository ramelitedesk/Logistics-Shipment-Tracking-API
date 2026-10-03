from app.core.shipment_status import ShipmentStatus


ALLOWED_SHIPMENT_TRANSITIONS = {
    ShipmentStatus.CREATED: {
        ShipmentStatus.CONFIRMED,
        ShipmentStatus.CANCELLED,
    },

    ShipmentStatus.CONFIRMED: {
        ShipmentStatus.PICKUP_SCHEDULED,
        ShipmentStatus.CANCELLED,
        ShipmentStatus.ON_HOLD,
    },

    ShipmentStatus.PICKUP_SCHEDULED: {
        ShipmentStatus.PICKED_UP,
        ShipmentStatus.CANCELLED,
        ShipmentStatus.ON_HOLD,
    },

    ShipmentStatus.PICKED_UP: {
        ShipmentStatus.AT_ORIGIN_WAREHOUSE,
        ShipmentStatus.IN_TRANSIT,
        ShipmentStatus.ON_HOLD,
    },

    ShipmentStatus.AT_ORIGIN_WAREHOUSE: {
        ShipmentStatus.IN_TRANSIT,
        ShipmentStatus.ON_HOLD,
    },

    ShipmentStatus.IN_TRANSIT: {
        ShipmentStatus.AT_DESTINATION_WAREHOUSE,
        ShipmentStatus.ON_HOLD,
        ShipmentStatus.LOST,
        ShipmentStatus.DAMAGED,
    },

    ShipmentStatus.AT_DESTINATION_WAREHOUSE: {
        ShipmentStatus.OUT_FOR_DELIVERY,
        ShipmentStatus.ON_HOLD,
    },

    ShipmentStatus.OUT_FOR_DELIVERY: {
        ShipmentStatus.DELIVERED,
        ShipmentStatus.DELIVERY_FAILED,
        ShipmentStatus.ON_HOLD,
    },

    ShipmentStatus.DELIVERY_FAILED: {
        ShipmentStatus.OUT_FOR_DELIVERY,
        ShipmentStatus.RETURN_INITIATED,
    },

    ShipmentStatus.RETURN_INITIATED: {
        ShipmentStatus.RETURNED,
    },

    ShipmentStatus.ON_HOLD: {
        ShipmentStatus.CONFIRMED,
        ShipmentStatus.PICKUP_SCHEDULED,
        ShipmentStatus.PICKED_UP,
        ShipmentStatus.AT_ORIGIN_WAREHOUSE,
        ShipmentStatus.IN_TRANSIT,
        ShipmentStatus.AT_DESTINATION_WAREHOUSE,
        ShipmentStatus.OUT_FOR_DELIVERY,
        ShipmentStatus.CANCELLED,
    },

    ShipmentStatus.DELIVERED: set(),
    ShipmentStatus.CANCELLED: set(),
    ShipmentStatus.RETURNED: set(),
    ShipmentStatus.LOST: set(),
    ShipmentStatus.DAMAGED: set(),
}