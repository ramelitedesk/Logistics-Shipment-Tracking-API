def test_shipment_summary_report(client, admin_headers):
    response = client.get(
        "/api/v1/reports/shipment-summary",
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert "total_shipments" in data
    assert "delivered" in data
    assert "total_exceptions" in data


def test_delivery_performance_report(client, admin_headers):
    response = client.get(
        "/api/v1/reports/delivery-performance",
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert "total_attempts" in data
    assert "successful_attempts" in data
    assert "success_rate" in data


def test_carrier_performance_report(client, admin_headers):
    response = client.get(
        "/api/v1/reports/carrier-performance",
        headers=admin_headers,
    )

    assert response.status_code == 200

    assert isinstance(response.json(), list)


def test_exception_report(client, admin_headers):
    response = client.get(
        "/api/v1/reports/exceptions",
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert "total_exceptions" in data
    assert "open_exceptions" in data
    assert "resolved_exceptions" in data