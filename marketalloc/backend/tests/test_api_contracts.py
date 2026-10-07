from fastapi.testclient import TestClient

from app.main import app


def test_swagger_redoc_openapi_and_frontend_cors_are_available():
    client = TestClient(app)
    assert client.get("/docs").status_code == 200
    assert client.get("/redoc").status_code == 200
    openapi = client.get("/openapi.json").json()
    assert "/api/attribution/calculate" in openapi["paths"]
    assert openapi["paths"]["/api/channels"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]["$ref"].endswith(
        "ChannelListResponse"
    )
    cors = client.options(
        "/api/channels",
        headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"},
    )
    assert cors.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_invalid_csv_upload_returns_actionable_validation_error():
    client = TestClient(app)
    response = client.post(
        "/api/data/upload",
        data={"dataset_type": "customers"},
        files={"file": ("customers.csv", b"wrong_column\nvalue\n", "text/csv")},
    )
    assert response.status_code == 400
    assert "missing required columns" in response.json()["detail"]


def test_budget_request_rejects_zero_budget_before_database_access():
    client = TestClient(app)
    response = client.post(
        "/api/budget/optimize",
        json={"total_budget": 0, "attribution_model": "linear"},
    )
    assert response.status_code == 422
