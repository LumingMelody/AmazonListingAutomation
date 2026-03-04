from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_import_ad_performance_endpoint() -> None:
    """测试广告数据导入接口"""
    response = client.post(
        "/api/analytics/import/ad-performance",
        json={
            "data": [
                {
                    "campaign_id": "CAMP001",
                    "impressions": 1000,
                    "clicks": 50,
                    "spend": "25.50",
                    "sales": "100.00",
                    "orders": 5,
                    "date": "2026-03-01",
                }
            ]
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["imported"] == 1


def test_import_listing_metrics_endpoint() -> None:
    """测试 Listing 指标导入接口"""
    response = client.post(
        "/api/analytics/import/listing-metrics",
        json={
            "data": [
                {
                    "asin": "B001",
                    "sku": "SKU001",
                    "sessions": 500,
                    "page_views": 800,
                    "units_ordered": 10,
                    "ordered_product_sales": "299.90",
                    "date": "2026-03-01",
                }
            ]
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["imported"] == 1


def test_get_metrics_summary() -> None:
    """测试获取指标汇总"""
    response = client.get("/api/analytics/metrics/summary?days=7")

    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "data" in data
