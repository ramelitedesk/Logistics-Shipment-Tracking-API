def test_api_clients_require_authentication(client):
    response = client.get(
        "/api/v1/api-clients/me"
    )

    assert response.status_code in (401, 403)


def test_list_api_clients(client, admin_headers):
    response = client.get(
        "/api/v1/api-clients/",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)