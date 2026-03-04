from decimal import Decimal

import pytest

from app.core.competitor_monitor_service import CompetitorMonitorService


@pytest.fixture
def monitor_service() -> CompetitorMonitorService:
    return CompetitorMonitorService()


def test_analyze_price_changes_decreasing(monitor_service: CompetitorMonitorService) -> None:
    """竞品价格明显下降应识别为 decreasing。"""
    historical_prices = [
        {"price": "120.00"},
        {"price": "118.00"},
        {"price": "119.00"},
        {"price": "121.00"},
        {"price": "117.00"},
        {"price": "120.00"},
        {"price": "118.00"},
    ]

    result = monitor_service.analyze_price_changes(
        asin="B00TEST001",
        current_price=Decimal("100.00"),
        historical_prices=historical_prices,
    )

    assert result["trend"] == "decreasing"
    assert result["change_percent"] < -5
    assert result["avg_price"] > result["current_price"]


def test_detect_rank_changes_declining(monitor_service: CompetitorMonitorService) -> None:
    """排名较历史均值恶化超过 100 位应识别为 declining。"""
    historical_ranks = [3200, 3150, 3180, 3220, 3190, 3170, 3160]

    result = monitor_service.detect_rank_changes(
        current_rank=3405,
        historical_ranks=historical_ranks,
    )

    assert result["status"] == "declining"
    assert result["change"] > 100
    assert result["current_rank"] == 3405


def test_generate_recommendations_with_price_and_rank_signals(
    monitor_service: CompetitorMonitorService,
) -> None:
    """当出现降价和排名下滑信号时，需生成两条建议。"""
    price_analysis = {
        "trend": "decreasing",
        "change_percent": -8.5,
        "avg_price": 120.0,
        "current_price": 109.8,
    }
    rank_analysis = {
        "status": "declining",
        "change": 156,
        "current_rank": 3405,
        "avg_rank": 3249,
    }

    recommendations = monitor_service.generate_recommendations(
        asin="B00TEST001",
        price_analysis=price_analysis,
        rank_analysis=rank_analysis,
    )

    assert len(recommendations) == 2
    assert recommendations[0]["type"] == "adjust_price"
    assert recommendations[0]["priority"] == "high"
    assert recommendations[1]["type"] == "increase_ads"
    assert recommendations[1]["priority"] == "medium"


def test_analyze_price_changes_without_history_returns_stable(
    monitor_service: CompetitorMonitorService,
) -> None:
    """无历史价格数据时应返回 stable。"""
    result = monitor_service.analyze_price_changes(
        asin="B00TEST001",
        current_price=Decimal("99.99"),
        historical_prices=[],
    )

    assert result == {"trend": "stable", "change_percent": 0}
