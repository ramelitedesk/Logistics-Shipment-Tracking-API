import traceback

from app.core.database import SessionLocal
from app.services.webhook_service import create_webhook
from app.schemas.webhook import WebhookCreate


print("Starting webhook test...")

db = SessionLocal()

try:
    data = WebhookCreate(
        carrier_id=1,
        shipment_id=1,
        event_type="SHIPMENT_STATUS_UPDATE",
        external_event_id="carrier-debug-002",
        payload='{"status":"CONFIRMED","location":"Bhubaneswar","facility":"Origin Hub","description":"Shipment confirmed by carrier."}',
        signature="test-signature",
    )

    print("Schema created successfully.")

    result = create_webhook(
        db=db,
        webhook_data=data,
    )

    print("SUCCESS:", result.id)

except Exception:
    print("ERROR OCCURRED:")
    traceback.print_exc()

finally:
    db.close()
