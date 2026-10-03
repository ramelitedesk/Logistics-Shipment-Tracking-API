def test_login_success(client, admin_credentials):
    response = client.post(
        "/api/v1/auth/login",
        data=admin_credentials,
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"].lower() == "bearer"


def test_login_invalid_password(client):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin@example.com",
            "password": "WrongPassword@999",
        },
    )

    assert response.status_code == 401


def test_invalid_token(client):
    response = client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert response.status_code == 401


def test_auth_me(client, admin_headers):
    response = client.get(
        "/api/v1/auth/me",
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == "admin@example.com"
    assert data["role"] == "SUPER_ADMIN"