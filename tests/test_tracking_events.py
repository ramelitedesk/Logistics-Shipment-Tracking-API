def test_tracking_requires_authentication(client):
    response = client.get(
        "/api/v1/tracking-events/shipment/999999"
    )

    assert response.status_code in (401, 403)


def test_tracking_nonexistent_shipment(client, admin_headers):
    response = client.get(
        "/api/v1/tracking-events/shipment/999999",
        headers=admin_headers,
    )

    assert response.status_code in (200, 404)