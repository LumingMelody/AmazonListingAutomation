from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_check_metrics_endpoint() -> None:
    """测试指标检查接口"""
    response = client.post(
        "/api/alerts/check",
        json={
            "metrics": {
                "asin": "B001",
                "sessions": 1000,
                "units_ordered": 5,
                "cvr": 0.005,
            }
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "alerts" in data
    assert isinstance(data["alerts"], list)


def test_get_active_alerts() -> None:
    """测试获取活跃预警"""
    response = client.get("/api/alerts/active")

    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "alerts" in data


def test_resolve_alert() -> None:
    """测试解决预警"""
    response = client.post(
        "/api/alerts/1/resolve",
        json={"reason": "已处理"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
