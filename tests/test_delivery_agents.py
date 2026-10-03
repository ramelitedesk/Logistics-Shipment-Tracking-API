def test_list_delivery_agents(client, admin_headers):
    response = client.get(
        "/api/v1/delivery-agents/",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_delivery_agent_me_requires_authentication(client):
    response = client.get(
        "/api/v1/delivery-agents/me"
    )

    assert response.status_code in (401, 403)