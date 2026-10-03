def test_list_users(client, admin_headers):
    response = client.get(
        "/api/v1/users/",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_user(client, admin_headers, unique_email):
    payload = {
        "email": unique_email,
        "password": "TestUser@12345",
        "full_name": "Pytest User",
        "role": "CUSTOMER",
    }

    response = client.post(
        "/api/v1/users/",
        json=payload,
        headers=admin_headers,
    )

    assert response.status_code == 201, response.text

    data = response.json()

    assert data["email"] == unique_email
    assert data["full_name"] == "Pytest User"
    assert data["role"] == "CUSTOMER"
    assert "password" not in data
    assert "password_hash" not in data


def test_create_duplicate_user(client, admin_headers, unique_email):
    payload = {
        "email": unique_email,
        "password": "TestUser@12345",
        "full_name": "Duplicate Test User",
        "role": "CUSTOMER",
    }

    first_response = client.post(
        "/api/v1/users/",
        json=payload,
        headers=admin_headers,
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/api/v1/users/",
        json=payload,
        headers=admin_headers,
    )

    assert second_response.status_code in (400, 409)