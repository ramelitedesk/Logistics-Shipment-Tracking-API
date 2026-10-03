def test_list_shipments_requires_authentication(client):
    response = client.get("/api/v1/shipments/")

    assert response.status_code in (401, 403)


def test_list_shipments_admin(client, admin_headers):
    response = client.get(
        "/api/v1/shipments/",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_nonexistent_shipment(client, admin_headers):
    response = client.get(
        "/api/v1/shipments/999999",
        headers=admin_headers,
    )

    assert response.status_code == 404