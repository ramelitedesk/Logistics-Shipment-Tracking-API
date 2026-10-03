def test_pod_requires_authentication(client):
    response = client.get(
        "/api/v1/proof-of-delivery/999999"
    )

    assert response.status_code in (401, 403)


def test_pod_nonexistent(client, admin_headers):
    response = client.get(
        "/api/v1/proof-of-delivery/999999",
        headers=admin_headers,
    )

    assert response.status_code == 404