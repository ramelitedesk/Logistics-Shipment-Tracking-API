from pydantic import BaseModel


class ShipmentSummaryResponse(BaseModel):
    total_shipments: int
    created: int
    confirmed: int
    pickup_scheduled: int
    picked_up: int
    at_origin_warehouse: int
    in_transit: int
    at_destination_warehouse: int
    out_for_delivery: int
    delivered: int
    cancelled: int
    on_hold: int
    delivery_failed: int
    return_initiated: int
    returned: int
    lost: int
    damaged: int
    total_exceptions: int


class DeliveryPerformanceResponse(BaseModel):
    total_attempts: int
    successful_attempts: int
    failed_attempts: int
    rescheduled_attempts: int
    success_rate: float
    failure_rate: float
    reschedule_rate: float


class CarrierPerformanceItem(BaseModel):
    carrier_id: int
    carrier_name: str
    total_shipments: int
    delivered_shipments: int
    failed_shipments: int
    delivered_rate: float


class ExceptionReportResponse(BaseModel):
    total_exceptions: int
    open_exceptions: int
    resolved_exceptions: int
    damaged: int
    lost: int
    address_issue: int
    customer_unavailable: int
    weather_delay: int
    other: int