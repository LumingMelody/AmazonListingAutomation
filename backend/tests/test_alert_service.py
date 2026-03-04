import pytest

from app.core.alert_service import AlertService


@pytest.fixture
def alert_service() -> AlertService:
    return AlertService()


def test_check_cvr_drop(alert_service: AlertService) -> None:
    """测试转化率下降预警"""
    metrics = {
        "asin": "B001",
        "sessions": 1000,
        "units_ordered": 5,
        "cvr": 0.005,
    }

    result = alert_service.check_metrics(metrics)
    assert "cvr_drop" in [a["type"] for a in result]


def test_check_refund_rate_spike(alert_service: AlertService) -> None:
    """测试退款率异常预警"""
    metrics = {
        "asin": "B001",
        "orders": 100,
        "refunds": 15,
        "refund_rate": 0.15,
    }

    result = alert_service.check_metrics(metrics)
    assert "refund_rate_spike" in [a["type"] for a in result]
