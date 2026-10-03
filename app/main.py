from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.customers import router as customers_router
from app.api.v1.addresses import router as addresses_router
from app.api.v1.orders import router as orders_router
from app.api.v1.shipments import router as shipments_router
from app.api.v1.tracking_events import router as tracking_events_router
from app.api.v1.carriers import router as carriers_router
from app.api.v1.warehouses import router as warehouse_router
from app.api.v1.delivery_agents import router as delivery_agents_router
from app.api.v1.shipment_assignments import (
    router as shipment_assignments_router,
)
from app.api.v1.delivery_attempts import router as delivery_attempts_router
from app.api.v1.proof_of_delivery import router as proof_of_delivery_router
from app.api.v1.shipment_exceptions import (
    router as shipment_exceptions_router,
)
from app.api.v1.notifications import (
    router as notifications_router,
)
from app.api.v1.webhooks import (
    router as webhooks_router,
)
from app.api.v1.audit_logs import router as audit_logs_router
from app.api.v1 import reports
from app.api.v1.api_clients import router as api_clients_router


app = FastAPI(
    title="Logistics & Shipment Tracking API",
    version="1.0.0",
    description="Backend API platform for logistics and shipment tracking.",
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

allowed_origins = [
    origin.strip()
    for origin in settings.cors_allowed_origins.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )

        return response


app.add_middleware(SecurityHeadersMiddleware)

# ============================================================
# GLOBAL EXCEPTION HANDLER
# ============================================================

@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error.",
        },
    )


# ============================================================
# API ROUTES
# ============================================================

app.include_router(
    auth_router,
    prefix="/api/v1",
)

app.include_router(
    users_router,
    prefix="/api/v1",
)

app.include_router(
    customers_router,
    prefix="/api/v1",
)

app.include_router(
    addresses_router,
    prefix="/api/v1",
)

app.include_router(
    orders_router,
    prefix="/api/v1",
)

app.include_router(
    shipments_router,
    prefix="/api/v1",
)

app.include_router(
    tracking_events_router,
    prefix="/api/v1",
)

app.include_router(
    carriers_router,
    prefix="/api/v1",
)

app.include_router(
    warehouse_router,
    prefix="/api/v1",
)

app.include_router(
    delivery_agents_router,
    prefix="/api/v1",
)

app.include_router(
    shipment_assignments_router,
    prefix="/api/v1",
)

app.include_router(
    delivery_attempts_router,
    prefix="/api/v1",
)

app.include_router(
    proof_of_delivery_router,
    prefix="/api/v1",
)

app.include_router(
    shipment_exceptions_router,
    prefix="/api/v1",
)

app.include_router(
    notifications_router,
    prefix="/api/v1",
)

app.include_router(
    webhooks_router,
    prefix="/api/v1",
)

app.include_router(
    audit_logs_router,
    prefix="/api/v1",
)

app.include_router(
    reports.router,
    prefix="/api/v1",
)

app.include_router(
    api_clients_router,
    prefix="/api/v1",
)


# ============================================================
# HEALTH CHECKS
# ============================================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "logistics-shipment-tracking-api",
    }


@app.get("/health/database")
def database_health_check():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))

    return {
        "status": "healthy",
        "database": "connected",
        "result": result.scalar(),
    }