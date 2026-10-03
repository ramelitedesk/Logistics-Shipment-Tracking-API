def test_notifications_require_authentication(client):
    response = client.get(
        "/api/v1/notifications/me"
    )

    assert response.status_code in (401, 403)


def test_notifications_admin(client, admin_headers):
    response = client.get(
        "/api/v1/notifications/me",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)