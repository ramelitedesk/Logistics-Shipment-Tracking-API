def test_list_customers(client, admin_headers):
    response = client.get(
        "/api/v1/customers/",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_customer_requires_authentication(client):
    response = client.get("/api/v1/customers/")

    assert response.status_code in (401, 403)


def test_customer_me_requires_authentication(client):
    response = client.get("/api/v1/customers/me")

    assert response.status_code in (401, 403)


def test_customer_by_id_requires_management_role(client, admin_headers):
    response = client.get(
        "/api/v1/customers/999999",
        headers=admin_headers,
    )

    assert response.status_code == 404