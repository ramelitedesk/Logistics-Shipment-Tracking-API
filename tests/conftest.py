import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def unique_email():
    return f"pytest_{uuid.uuid4().hex[:10]}@example.com"


@pytest.fixture
def admin_credentials():
    return {
        "username": "admin@example.com",
        "password": "Admin@12345",
    }


@pytest.fixture
def admin_token(client, admin_credentials):
    response = client.post(
        "/api/v1/auth/login",
        data=admin_credentials,
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert "access_token" in data
    assert data["token_type"].lower() == "bearer"

    return data["access_token"]


@pytest.fixture
def admin_headers(admin_token):
    return {
        "Authorization": f"Bearer {admin_token}",
    }