def test_exceptions_require_authentication(client):
    response = client.get(
        "/api/v1/shipment-exceptions/"
    )

    assert response.status_code in (401, 403)


def test_exception_nonexistent(client, admin_headers):
    response = client.get(
        "/api/v1/shipment-exceptions/999999",
        headers=admin_headers,
    )

    assert response.status_code == 404