import pytest

from app.core.experiment_service import ExperimentService


@pytest.fixture
def experiment_service() -> ExperimentService:
    return ExperimentService()


def test_evaluate_listing_insufficient_sample(experiment_service: ExperimentService) -> None:
    """测试样本量不足的情况。"""
    metrics = {
        "sessions": 50,
        "orders": 3,
        "cvr": 0.06,
        "refund_rate": 0.05,
        "sales": 150,
    }

    result = experiment_service.evaluate_listing(metrics)

    assert result["decision"] == "continue_test"
    assert result["stage"] == "test"
    assert result["score"] == 0.0


def test_evaluate_listing_excellent_performance(experiment_service: ExperimentService) -> None:
    """测试优秀表现。"""
    metrics = {
        "sessions": 1000,
        "orders": 50,
        "cvr": 0.05,
        "refund_rate": 0.03,
        "sales": 1500,
    }

    result = experiment_service.evaluate_listing(metrics)

    assert result["decision"] == "add_variants"
    assert result["stage"] == "scale"
    assert result["score"] >= 80.0


def test_evaluate_listing_poor_performance(experiment_service: ExperimentService) -> None:
    """测试差劲表现。"""
    metrics = {
        "sessions": 1000,
        "orders": 10,
        "cvr": 0.005,
        "refund_rate": 0.15,
        "sales": 200,
    }

    result = experiment_service.evaluate_listing(metrics)

    assert result["decision"] == "discontinue"
    assert result["stage"] == "eliminate"
    assert result["score"] < 40.0
