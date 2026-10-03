def test_list_carriers(client, admin_headers):
    response = client.get(
        "/api/v1/carriers/",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_carrier(client, admin_headers):
    payload = {
        "name": "Pytest Carrier",
        "code": "PYTEST",
        "contact_email": "carrier@example.com",
        "contact_phone": "+919999999999",
        "api_base_url": "https://example.com/api",
        "is_active": True,
        "description": "Automated test carrier",
    }

    response = client.post(
        "/api/v1/carriers/",
        json=payload,
        headers=admin_headers,
    )

    assert response.status_code == 201, response.text

    data = response.json()

    assert data["name"] == "Pytest Carrier"
    assert data["code"] == "PYTEST"
    assert data["is_active"] is True