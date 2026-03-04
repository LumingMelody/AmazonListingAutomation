from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_check_text_endpoint() -> None:
    response = client.post(
        "/api/compliance/check-text",
        json={"text": "Nike shoes for sale", "context": {}},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["risk_level"] in ["high", "critical"]


def test_check_listing_endpoint() -> None:
    response = client.post(
        "/api/compliance/check-listing",
        json={
            "listing_data": {
                "title": "High Quality Running Shoes for Men",
                "bullet_points": [
                    "Breathable and lightweight design for all-day comfort",
                    "Durable sole suitable for road and gym training",
                    "Non-slip outsole improves traction on wet surfaces",
                ],
                "description": "A durable pair of running shoes designed for daily exercise.",
                "main_image": "image.jpg",
                "price": 29.99,
            }
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["overall_status"] in ["pass", "warning", "blocked", "fail"]


def test_batch_check_endpoint() -> None:
    response = client.post(
        "/api/compliance/batch-check",
        json={
            "items": [
                {"title": "Nike shoes", "description": "Great product", "main_image": "a.jpg", "price": 10},
                {"title": "Clean title for listing", "description": "Simple description", "main_image": "b.png", "price": 20},
            ]
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["total"] == 2
    assert len(data["data"]["results"]) == 2
