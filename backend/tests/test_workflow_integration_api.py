from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_excel_process_blocks_high_risk_listing() -> None:
    response = client.post(
        "/api/process",
        json={
            "mode": "add-color",
            "template_type": "DaMaUS",
            "skus": ["TEST001"],
            "product_info": {
                "title": "Nike shoes for sale",
                "description": "High quality product",
            },
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["requires_approval"] is True
    assert data["compliance_result"]["risk_level"] in ["high", "critical"]


def test_excel_process_passes_clean_listing() -> None:
    response = client.post(
        "/api/process",
        json={
            "mode": "add-color",
            "template_type": "DaMaUS",
            "skus": ["TEST001"],
            "product_info": {
                "title": "High quality running shoes for men",
                "description": "Comfortable and durable product for daily use",
            },
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "qa_result" in data


def test_followsell_process_blocks_high_risk_old_listing() -> None:
    response = client.post(
        "/api/followsell/process",
        json={
            "old_file": "Nike old listing.xlsx",
            "new_file": "new listing.xlsx",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["requires_approval"] is True


def test_followsell_process_passes_clean_old_listing() -> None:
    response = client.post(
        "/api/followsell/process",
        json={
            "old_file": "clean old listing.xlsx",
            "new_file": "new listing.xlsx",
            "old_listing_text": "generic sports shoes no brand mention",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "compliance_result" in data
