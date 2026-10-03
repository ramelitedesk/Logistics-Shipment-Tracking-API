from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.dependencies import require_role
from app.core.database import get_db
from app.core.roles import UserRole
from app.schemas.report import (
    CarrierPerformanceItem,
    DeliveryPerformanceResponse,
    ExceptionReportResponse,
    ShipmentSummaryResponse,
)
from app.services.report_service import (
    get_carrier_performance,
    get_delivery_performance,
    get_exception_report,
    get_shipment_summary,
)

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


@router.get(
    "/shipment-summary",
    response_model=ShipmentSummaryResponse,
)
def shipment_summary(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(
            UserRole.SUPER_ADMIN,
            UserRole.OPERATIONS_MANAGER,
        )
    ),
):
    return get_shipment_summary(db)


@router.get(
    "/delivery-performance",
    response_model=DeliveryPerformanceResponse,
)
def delivery_performance(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(
            UserRole.SUPER_ADMIN,
            UserRole.OPERATIONS_MANAGER,
        )
    ),
):
    return get_delivery_performance(db)


@router.get(
    "/carrier-performance",
    response_model=list[CarrierPerformanceItem],
)
def carrier_performance(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(
            UserRole.SUPER_ADMIN,
            UserRole.OPERATIONS_MANAGER,
        )
    ),
):
    return get_carrier_performance(db)


@router.get(
    "/exceptions",
    response_model=ExceptionReportResponse,
)
def exception_report(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(
            UserRole.SUPER_ADMIN,
            UserRole.OPERATIONS_MANAGER,
        )
    ),
):
    return get_exception_report(db)