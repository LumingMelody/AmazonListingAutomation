from decimal import Decimal
from typing import Any, Dict


class ExperimentService:
    """测试款自动分层服务。"""

    THRESHOLDS = {
        "min_sessions": 100,
        "min_orders": 10,
        "cvr_min": Decimal("0.01"),
        "cvr_good": Decimal("0.03"),
        "refund_rate_max": Decimal("0.10"),
        "score_eliminate": Decimal("40.0"),
        "score_observe": Decimal("60.0"),
        "score_scale": Decimal("80.0"),
    }

    def evaluate_listing(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """评估 Listing 指标并给出分层决策。"""
        if not self._has_sufficient_sample(metrics):
            return {
                "decision": "continue_test",
                "stage": "test",
                "score": 0.0,
                "reason": "样本量不足，继续测试",
            }

        score = self._calculate_score(metrics)
        stage = self._determine_stage(score)
        decision = self._make_decision(stage)

        return {
            "decision": decision,
            "stage": stage,
            "score": float(score),
            "reason": self._generate_reason(decision, metrics),
        }

    def _has_sufficient_sample(self, metrics: Dict[str, Any]) -> bool:
        return metrics.get("sessions", 0) >= self.THRESHOLDS["min_sessions"] and metrics.get("orders", 0) >= self.THRESHOLDS[
            "min_orders"
        ]

    def _calculate_score(self, metrics: Dict[str, Any]) -> Decimal:
        score = Decimal("0")

        cvr = Decimal(str(metrics.get("cvr", 0)))
        if cvr >= self.THRESHOLDS["cvr_good"]:
            score += Decimal("40")
        elif cvr >= self.THRESHOLDS["cvr_min"]:
            score += Decimal("20")

        refund_rate = Decimal(str(metrics.get("refund_rate", 0)))
        if refund_rate <= self.THRESHOLDS["refund_rate_max"]:
            score += Decimal("30")

        sales = Decimal(str(metrics.get("sales", 0)))
        if sales > 1000:
            score += Decimal("30")
        elif sales > 500:
            score += Decimal("15")

        return score

    def _determine_stage(self, score: Decimal) -> str:
        if score >= self.THRESHOLDS["score_scale"]:
            return "scale"
        if score >= self.THRESHOLDS["score_observe"]:
            return "observe"
        if score >= self.THRESHOLDS["score_eliminate"]:
            return "test"
        return "eliminate"

    def _make_decision(self, stage: str) -> str:
        decisions = {
            "scale": "add_variants",
            "observe": "continue_monitor",
            "test": "continue_test",
            "eliminate": "discontinue",
        }
        return decisions.get(stage, "continue_test")

    def _generate_reason(self, decision: str, metrics: Dict[str, Any]) -> str:
        reasons = {
            "add_variants": f"表现优秀（CVR: {metrics.get('cvr', 0):.2%}），建议加色加码",
            "continue_monitor": "表现良好，继续观察数据",
            "continue_test": "样本量充足，继续测试",
            "discontinue": f"表现不佳（CVR: {metrics.get('cvr', 0):.2%}），建议下架",
        }
        return reasons.get(decision, "继续测试")
