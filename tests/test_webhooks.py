def test_webhooks_require_authentication(client):
    response = client.get(
        "/api/v1/webhooks/"
    )

    assert response.status_code in (401, 403)


def test_webhook_nonexistent(client, admin_headers):
    response = client.get(
        "/api/v1/webhooks/999999",
        headers=admin_headers,
    )

    assert response.status_code == 404