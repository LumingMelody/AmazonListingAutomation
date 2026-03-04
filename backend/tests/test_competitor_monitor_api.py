from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_track_competitor_endpoint_returns_price_and_rank_analysis() -> None:
    response = client.post(
        "/api/competitor-monitor/track",
        json={
            "asin": "B00TARGET01",
            "competitor_asin": "B00COMP001",
            "current_price": "99.00",
            "historical_prices": [
                {"price": "108.00"},
                {"price": "107.50"},
                {"price": "106.00"},
                {"price": "105.00"},
            ],
            "current_rank": 3250,
            "historical_ranks": [3000, 3010, 3025, 3030],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["asin"] == "B00TARGET01"
    assert payload["competitor_asin"] == "B00COMP001"
    assert payload["price_analysis"]["trend"] == "decreasing"
    assert payload["rank_analysis"]["status"] == "declining"


def test_price_analysis_endpoint_returns_decreasing_trend() -> None:
    response = client.post(
        "/api/competitor-monitor/price-analysis",
        json={
            "asin": "B00TARGET01",
            "current_price": "100.00",
            "historical_prices": [
                {"price": "115.00"},
                {"price": "112.00"},
                {"price": "114.00"},
                {"price": "113.00"},
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["analysis"]["trend"] == "decreasing"
    assert payload["analysis"]["change_percent"] < -5


def test_recommendations_endpoint_returns_action_suggestions() -> None:
    response = client.post(
        "/api/competitor-monitor/recommendations",
        json={
            "asin": "B00TARGET01",
            "price_analysis": {
                "trend": "decreasing",
                "change_percent": -8.2,
                "avg_price": 110.0,
                "current_price": 101.0,
            },
            "rank_analysis": {
                "status": "declining",
                "change": 220,
                "current_rank": 3520,
                "avg_rank": 3300,
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["recommendations"]) == 2
    assert payload["recommendations"][0]["type"] == "adjust_price"
    assert payload["recommendations"][1]["type"] == "increase_ads"
