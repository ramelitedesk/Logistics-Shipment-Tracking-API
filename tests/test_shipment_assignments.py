def test_assignments_require_authentication(client):
    response = client.get(
        "/api/v1/shipment-assignments/"
    )

    assert response.status_code in (401, 403)


def test_shipment_assignment_nonexistent(client, admin_headers):
    response = client.get(
        "/api/v1/shipment-assignments/999999",
        headers=admin_headers,
    )

    assert response.status_code == 404