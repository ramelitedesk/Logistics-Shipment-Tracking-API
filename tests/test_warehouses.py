def test_list_warehouses(client, admin_headers):
    response = client.get(
        "/api/v1/warehouses/",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_warehouse(client, admin_headers):
    payload = {
        "name": "Pytest Warehouse",
        "code": "PYWH001",
        "address_line1": "100 Test Street",
        "address_line2": None,
        "city": "Bhubaneswar",
        "state": "Odisha",
        "postal_code": "751001",
        "country": "India",
        "contact_phone": "+919999999999",
        "contact_email": "warehouse@example.com",
        "is_active": True,
        "description": "Automated test warehouse",
    }

    response = client.post(
        "/api/v1/warehouses/",
        json=payload,
        headers=admin_headers,
    )

    assert response.status_code == 201, response.text

    data = response.json()

    assert data["name"] == "Pytest Warehouse"
    assert data["code"] == "PYWH001"