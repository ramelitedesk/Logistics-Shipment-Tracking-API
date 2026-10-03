import uuid
from decimal import Decimal

from fastapi.testclient import TestClient


def unique_value(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def create_customer(
    client: TestClient,
    admin_headers: dict,
):
    email = f"workflow_customer_{uuid.uuid4().hex[:8]}@example.com"

    user_payload = {
        "email": email,
        "password": "WorkflowUser@12345",
        "full_name": "Workflow Customer",
        "role": "CUSTOMER",
    }

    user_response = client.post(
        "/api/v1/users/",
        json=user_payload,
        headers=admin_headers,
    )

    assert user_response.status_code == 201, user_response.text

    user = user_response.json()

    customer_payload = {
        "user_id": user["id"],
        "phone": "+919999999999",
        "company_name": "Workflow Test Company",
    }

    customer_response = client.post(
        "/api/v1/customers/",
        json=customer_payload,
        headers=admin_headers,
    )

    assert customer_response.status_code == 201, customer_response.text

    return user, customer_response.json()


def create_order(
    client: TestClient,
    admin_headers: dict,
    customer_id: int,
):
    order_payload = {
        "customer_id": customer_id,
        "order_number": unique_value("WF-ORDER"),
        "notes": "Automated end-to-end workflow test",
        "items": [
            {
                "product_name": "Workflow Test Product",
                "quantity": 2,
                "unit_price": 500.00,
            }
        ],
    }

    response = client.post(
        "/api/v1/orders/",
        json=order_payload,
        headers=admin_headers,
    )

    assert response.status_code == 201, response.text

    return response.json()


def create_warehouse(
    client: TestClient,
    admin_headers: dict,
    prefix: str,
):
    payload = {
        "name": unique_value(f"{prefix}_Warehouse"),
        "code": unique_value(prefix.upper())[:20],
        "address_line1": "100 Workflow Street",
        "address_line2": None,
        "city": "Bhubaneswar",
        "state": "Odisha",
        "postal_code": "751001",
        "country": "India",
        "contact_phone": "+919999999999",
        "contact_email": f"{prefix.lower()}@example.com",
        "is_active": True,
        "description": "Automated workflow test warehouse",
    }

    response = client.post(
        "/api/v1/warehouses/",
        json=payload,
        headers=admin_headers,
    )

    assert response.status_code == 201, response.text

    return response.json()


def create_carrier(
    client: TestClient,
    admin_headers: dict,
):
    payload = {
        "name": unique_value("Workflow Carrier"),
        "code": unique_value("WFC").upper()[:20],
        "contact_email": "workflow-carrier@example.com",
        "contact_phone": "+919999999998",
        "api_base_url": "https://example.com/api",
        "is_active": True,
        "description": "Automated workflow test carrier",
    }

    response = client.post(
        "/api/v1/carriers/",
        json=payload,
        headers=admin_headers,
    )

    assert response.status_code == 201, response.text

    return response.json()


def create_delivery_agent(
    client: TestClient,
    admin_headers: dict,
):
    email = f"workflow_agent_{uuid.uuid4().hex[:8]}@example.com"

    user_payload = {
        "email": email,
        "password": "WorkflowAgent@12345",
        "full_name": "Workflow Delivery Agent",
        "role": "DELIVERY_AGENT",
    }

    user_response = client.post(
        "/api/v1/users/",
        json=user_payload,
        headers=admin_headers,
    )

    assert user_response.status_code == 201, user_response.text

    user = user_response.json()

    agent_payload = {
        "user_id": user["id"],
        "employee_code": unique_value("AGENT").upper(),
        "phone": "+919999999997",
        "vehicle_type": "VAN",
        "vehicle_number": "OD-01-WF-0001",
        "license_number": unique_value("LIC"),
        "is_available": True,
        "is_active": True,
        "notes": "Created by automated workflow test",
    }

    agent_response = client.post(
        "/api/v1/delivery-agents/",
        json=agent_payload,
        headers=admin_headers,
    )

    assert agent_response.status_code == 201, agent_response.text

    return agent_response.json()


def test_complete_logistics_workflow(
    client: TestClient,
    admin_headers: dict,
):
    # ---------------------------------------------------------
    # 1. Create customer
    # ---------------------------------------------------------

    customer_user, customer = create_customer(
        client,
        admin_headers,
    )

    assert customer["user_id"] == customer_user["id"]

    # ---------------------------------------------------------
    # 2. Create order
    # ---------------------------------------------------------

    order = create_order(
        client,
        admin_headers,
        customer["id"],
    )

    assert order["customer_id"] == customer["id"]
    assert order["status"] == "PENDING"
    assert len(order["items"]) == 1

    order_id = order["id"]

    # ---------------------------------------------------------
    # 3. Confirm order
    # ---------------------------------------------------------

    response = client.patch(
        f"/api/v1/orders/{order_id}",
        json={
            "status": "CONFIRMED",
        },
        headers=admin_headers,
    )

    assert response.status_code == 200, response.text
    assert response.json()["status"] == "CONFIRMED"

    # ---------------------------------------------------------
    # 4. Move order to PROCESSING
    # ---------------------------------------------------------

    response = client.patch(
        f"/api/v1/orders/{order_id}",
        json={
            "status": "PROCESSING",
        },
        headers=admin_headers,
    )

    assert response.status_code == 200, response.text
    assert response.json()["status"] == "PROCESSING"

    # ---------------------------------------------------------
    # 5. Move order to READY_FOR_SHIPMENT
    # ---------------------------------------------------------

    response = client.patch(
        f"/api/v1/orders/{order_id}",
        json={
            "status": "READY_FOR_SHIPMENT",
        },
        headers=admin_headers,
    )

    assert response.status_code == 200, response.text
    assert response.json()["status"] == "READY_FOR_SHIPMENT"

    # ---------------------------------------------------------
    # 6. Create origin warehouse
    # ---------------------------------------------------------

    origin_warehouse = create_warehouse(
        client,
        admin_headers,
        "Origin",
    )

    assert origin_warehouse["is_active"] is True

    # ---------------------------------------------------------
    # 7. Create destination warehouse
    # ---------------------------------------------------------

    destination_warehouse = create_warehouse(
        client,
        admin_headers,
        "Destination",
    )

    assert destination_warehouse["is_active"] is True

    # ---------------------------------------------------------
    # 8. Create carrier
    # ---------------------------------------------------------

    carrier = create_carrier(
        client,
        admin_headers,
    )

    assert carrier["is_active"] is True

    # ---------------------------------------------------------
    # 9. Create shipment
    # ---------------------------------------------------------

    shipment_payload = {
        "order_id": order_id,
        "shipment_number": unique_value("WF-SHIP"),
        "tracking_number": unique_value("WF-TRACK"),
        "origin_warehouse_id": origin_warehouse["id"],
        "destination_warehouse_id": destination_warehouse["id"],
        "carrier_id": carrier["id"],
    }

    shipment_response = client.post(
        "/api/v1/shipments/",
        json=shipment_payload,
        headers=admin_headers,
    )

    assert shipment_response.status_code == 201, shipment_response.text

    shipment = shipment_response.json()

    assert shipment["order_id"] == order_id
    assert shipment["status"] == "CREATED"
    assert shipment["origin_warehouse_id"] == origin_warehouse["id"]
    assert shipment["destination_warehouse_id"] == destination_warehouse["id"]
    # assert shipment["carrier_id"] == carrier["id"]

    shipment_id = shipment["id"]

    # ---------------------------------------------------------
    # 10. Shipment CREATED -> CONFIRMED
    # ---------------------------------------------------------

    response = client.patch(
        f"/api/v1/shipments/{shipment_id}",
        json={
            "status": "CONFIRMED",
        },
        headers=admin_headers,
    )

    assert response.status_code == 200, response.text
    assert response.json()["status"] == "CONFIRMED"

    # ---------------------------------------------------------
    # 11. CONFIRMED -> PICKUP_SCHEDULED
    # ---------------------------------------------------------

    response = client.patch(
        f"/api/v1/shipments/{shipment_id}",
        json={
            "status": "PICKUP_SCHEDULED",
        },
        headers=admin_headers,
    )

    assert response.status_code == 200, response.text
    assert response.json()["status"] == "PICKUP_SCHEDULED"

    # ---------------------------------------------------------
    # 12. PICKUP_SCHEDULED -> PICKED_UP
    # ---------------------------------------------------------

    response = client.patch(
        f"/api/v1/shipments/{shipment_id}",
        json={
            "status": "PICKED_UP",
        },
        headers=admin_headers,
    )

    assert response.status_code == 200, response.text
    assert response.json()["status"] == "PICKED_UP"

    # ---------------------------------------------------------
    # 13. PICKED_UP -> AT_ORIGIN_WAREHOUSE
    # ---------------------------------------------------------

    response = client.patch(
        f"/api/v1/shipments/{shipment_id}",
        json={
            "status": "AT_ORIGIN_WAREHOUSE",
        },
        headers=admin_headers,
    )

    assert response.status_code == 200, response.text
    assert response.json()["status"] == "AT_ORIGIN_WAREHOUSE"

    # ---------------------------------------------------------
    # 14. AT_ORIGIN_WAREHOUSE -> IN_TRANSIT
    # ---------------------------------------------------------

    response = client.patch(
        f"/api/v1/shipments/{shipment_id}",
        json={
            "status": "IN_TRANSIT",
        },
        headers=admin_headers,
    )

    assert response.status_code == 200, response.text
    assert response.json()["status"] == "IN_TRANSIT"

    # ---------------------------------------------------------
    # 15. IN_TRANSIT -> AT_DESTINATION_WAREHOUSE
    # ---------------------------------------------------------

    response = client.patch(
        f"/api/v1/shipments/{shipment_id}",
        json={
            "status": "AT_DESTINATION_WAREHOUSE",
        },
        headers=admin_headers,
    )

    assert response.status_code == 200, response.text
    assert response.json()["status"] == "AT_DESTINATION_WAREHOUSE"

    # ---------------------------------------------------------
    # 16. Create delivery agent
    # ---------------------------------------------------------

    agent = create_delivery_agent(
        client,
        admin_headers,
    )

    assert agent["is_active"] is True

    # ---------------------------------------------------------
    # 17. Assign shipment to delivery agent
    # ---------------------------------------------------------

    assignment_payload = {
        "shipment_id": shipment_id,
        "delivery_agent_id": agent["id"],
    }

    assignment_response = client.post(
        "/api/v1/shipment-assignments/",
        json=assignment_payload,
        headers=admin_headers,
    )

    assert assignment_response.status_code == 201, (
        assignment_response.text
    )

    assignment = assignment_response.json()

    assert assignment["shipment_id"] == shipment_id
    assert assignment["delivery_agent_id"] == agent["id"]
    assert assignment["is_active"] is True

    # ---------------------------------------------------------
    # 18. AT_DESTINATION_WAREHOUSE -> OUT_FOR_DELIVERY
    # ---------------------------------------------------------

    response = client.patch(
        f"/api/v1/shipments/{shipment_id}",
        json={
            "status": "OUT_FOR_DELIVERY",
        },
        headers=admin_headers,
    )

    assert response.status_code == 200, response.text
    assert response.json()["status"] == "OUT_FOR_DELIVERY"

    # ---------------------------------------------------------
    # 19. Create successful delivery attempt
    # ---------------------------------------------------------

    attempt_payload = {
        "shipment_id": shipment_id,
        "delivery_agent_id": agent["id"],
        "status": "SUCCESS",
        "notes": "Delivered successfully during automated test",
    }

    attempt_response = client.post(
        "/api/v1/delivery-attempts/",
        json=attempt_payload,
        headers=admin_headers,
    )

    assert attempt_response.status_code == 201, (
        attempt_response.text
    )

    attempt = attempt_response.json()

    assert attempt["shipment_id"] == shipment_id
    assert attempt["delivery_agent_id"] == agent["id"]
    assert attempt["attempt_number"] == 1
    assert attempt["status"] == "SUCCESS"

    attempt_id = attempt["id"]

    # ---------------------------------------------------------
    # 20. OUT_FOR_DELIVERY -> DELIVERED
    # ---------------------------------------------------------

    response = client.patch(
        f"/api/v1/shipments/{shipment_id}",
        json={
            "status": "DELIVERED",
        },
        headers=admin_headers,
    )

    assert response.status_code == 200, response.text
    assert response.json()["status"] == "DELIVERED"

    # ---------------------------------------------------------
    # 21. Create Proof of Delivery
    # ---------------------------------------------------------

    pod_payload = {
        "shipment_id": shipment_id,
        "delivery_attempt_id": attempt_id,
        "recipient_name": "Workflow Recipient",
        "signature_reference": "workflow-signature-001",
        "photo_reference": "workflow-photo-001",
        "notes": "Automated POD test",
    }

    pod_response = client.post(
        "/api/v1/proof-of-delivery/",
        json=pod_payload,
        headers=admin_headers,
    )

    assert pod_response.status_code == 201, pod_response.text

    pod = pod_response.json()

    assert pod["shipment_id"] == shipment_id
    assert pod["delivery_attempt_id"] == attempt_id
    assert pod["recipient_name"] == "Workflow Recipient"

    # ---------------------------------------------------------
    # 22. Verify tracking timeline
    # ---------------------------------------------------------

    tracking_response = client.get(
        f"/api/v1/tracking-events/shipment/{shipment_id}",
        headers=admin_headers,
    )

    assert tracking_response.status_code == 200, (
        tracking_response.text
    )

    tracking_events = tracking_response.json()

    statuses = [
        event["status"]
        for event in tracking_events
    ]

    assert "CONFIRMED" in statuses
    assert "PICKUP_SCHEDULED" in statuses
    assert "PICKED_UP" in statuses
    assert "AT_ORIGIN_WAREHOUSE" in statuses
    assert "IN_TRANSIT" in statuses
    assert "AT_DESTINATION_WAREHOUSE" in statuses
    assert "OUT_FOR_DELIVERY" in statuses
    assert "DELIVERED" in statuses

    # ---------------------------------------------------------
    # 23. Verify customer notifications
    # ---------------------------------------------------------

    notification_response = client.get(
        f"/api/v1/notifications/user/{customer_user['id']}",
        headers=admin_headers,
    )

    assert notification_response.status_code == 200, (
        notification_response.text
    )

    notifications = notification_response.json()

    shipment_notifications = [
        notification
        for notification in notifications
        if notification.get("shipment_id") == shipment_id
    ]

    assert len(shipment_notifications) >= 1

    notification_statuses = {
        notification["status"]
        for notification in shipment_notifications
    }

    assert notification_statuses.intersection(
        {"PENDING", "SENT", "READ"}
    )

    # ---------------------------------------------------------
    # Final verification
    # ---------------------------------------------------------

    shipment_response = client.get(
        f"/api/v1/shipments/{shipment_id}",
        headers=admin_headers,
    )

    assert shipment_response.status_code == 200

    final_shipment = shipment_response.json()

    assert final_shipment["status"] == "DELIVERED"