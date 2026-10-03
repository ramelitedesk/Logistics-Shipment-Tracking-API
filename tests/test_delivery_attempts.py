def test_delivery_attempts_require_authentication(client):
    response = client.get(
        "/api/v1/delivery-attempts/"
    )

    assert response.status_code in (401, 403)


def test_delivery_attempt_nonexistent(client, admin_headers):
    response = client.get(
        "/api/v1/delivery-attempts/999999",
        headers=admin_headers,
    )

    assert response.status_code == 404