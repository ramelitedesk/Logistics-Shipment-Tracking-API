def test_list_orders_requires_authentication(client):
    response = client.get("/api/v1/orders/")

    assert response.status_code in (401, 403)


def test_list_orders_admin(client, admin_headers):
    response = client.get(
        "/api/v1/orders/",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)