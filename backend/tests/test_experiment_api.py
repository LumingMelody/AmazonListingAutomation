from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_evaluate_listing_endpoint() -> None:
    response = client.post(
        "/api/experiments/evaluate-listing",
        json={
            "metrics": {
                "sessions": 1200,
                "orders": 60,
                "cvr": 0.05,
                "refund_rate": 0.02,
                "sales": 1800,
            }
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "add_variants"
    assert data["stage"] == "scale"
    assert data["score"] >= 80


def test_lifecycle_create_list_and_update() -> None:
    asin = "B00TASK4A1"

    create_response = client.post(
        "/api/experiments/lifecycle",
        json={
            "asin": asin,
            "sku": "SKU-TASK4-A1",
            "status": "testing",
            "stage": "test",
            "sessions_total": 300,
            "orders_total": 18,
            "cvr": 0.06,
            "refund_rate": 0.03,
        },
    )

    assert create_response.status_code == 200
    created = create_response.json()
    assert created["success"] is True
    assert created["data"]["asin"] == asin
    assert created["data"]["status"] == "testing"

    list_response = client.get(f"/api/experiments/lifecycle?asin={asin}&status=testing")
    assert list_response.status_code == 200
    listed = list_response.json()
    assert listed["success"] is True
    assert len(listed["items"]) == 1
    assert listed["items"][0]["asin"] == asin

    update_response = client.patch(
        f"/api/experiments/lifecycle/{asin}",
        json={
            "status": "active",
            "stage": "scale",
            "decision": "add_variants",
            "decision_reason": "表现优秀",
        },
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["success"] is True
    assert updated["data"]["status"] == "active"
    assert updated["data"]["stage"] == "scale"


def test_generate_recommendations_endpoint() -> None:
    response = client.post(
        "/api/experiments/recommendations",
        json={
            "asin": "B00TASK4R1",
            "price_analysis": {
                "trend": "decreasing",
                "change_percent": -9.2,
                "avg_price": 120.0,
                "current_price": 109.0,
            },
            "rank_analysis": {
                "status": "declining",
                "change": 145,
                "current_rank": 3500,
                "avg_rank": 3355,
            },
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["recommendations"]) == 2
    assert data["recommendations"][0]["type"] == "adjust_price"
    assert data["recommendations"][1]["type"] == "increase_ads"
