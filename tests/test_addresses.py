def test_addresses_requires_authentication(client):
    response = client.get(
        "/api/v1/addresses/customer/1"
    )

    assert response.status_code in (401, 403)


def test_address_customer_endpoint_with_admin(client, admin_headers):
    response = client.get(
        "/api/v1/addresses/customer/999999",
        headers=admin_headers,
    )

    assert response.status_code in (200, 404)