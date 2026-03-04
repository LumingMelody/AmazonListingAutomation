from typing import Any, Dict, List


class AlertService:
    """预警服务。"""

    THRESHOLDS = {
        "cvr_min": 0.01,
        "refund_rate_max": 0.10,
        "chargeback_rate_max": 0.02,
    }

    def check_metrics(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检查指标并生成预警。"""
        alerts: List[Dict[str, Any]] = []

        if "cvr" in metrics and metrics["cvr"] < self.THRESHOLDS["cvr_min"]:
            alerts.append(
                {
                    "type": "cvr_drop",
                    "severity": "high",
                    "message": f"转化率过低: {metrics['cvr']:.2%}",
                    "asin": metrics.get("asin"),
                }
            )

        if "refund_rate" in metrics and metrics["refund_rate"] > self.THRESHOLDS["refund_rate_max"]:
            alerts.append(
                {
                    "type": "refund_rate_spike",
                    "severity": "critical",
                    "message": f"退款率异常: {metrics['refund_rate']:.2%}",
                    "asin": metrics.get("asin"),
                }
            )

        return alerts
