from decimal import Decimal
from typing import Any, Dict, List


class CompetitorMonitorService:
    """竞品监控服务。"""

    def analyze_price_changes(
        self,
        asin: str,
        current_price: Decimal,
        historical_prices: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """分析竞品价格趋势。"""
        _ = asin

        if not historical_prices:
            return {"trend": "stable", "change_percent": 0}

        recent_prices = [
            Decimal(str(item["price"]))
            for item in historical_prices[-7:]
            if item.get("price") is not None
        ]

        if not recent_prices:
            return {"trend": "stable", "change_percent": 0}

        avg_price = sum(recent_prices) / Decimal(len(recent_prices))
        change_percent = ((current_price - avg_price) / avg_price) * Decimal("100")

        if change_percent > Decimal("5"):
            trend = "increasing"
        elif change_percent < Decimal("-5"):
            trend = "decreasing"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "change_percent": float(change_percent),
            "avg_price": float(avg_price),
            "current_price": float(current_price),
        }

    def detect_rank_changes(
        self,
        current_rank: int,
        historical_ranks: List[int],
    ) -> Dict[str, Any]:
        """检测竞品排名变化。"""
        if not historical_ranks:
            return {"status": "new", "change": 0}

        recent_ranks = historical_ranks[-7:]
        avg_rank = sum(recent_ranks) / len(recent_ranks)
        change = current_rank - avg_rank

        if change < -100:
            status = "improving"
        elif change > 100:
            status = "declining"
        else:
            status = "stable"

        return {
            "status": status,
            "change": int(change),
            "current_rank": current_rank,
            "avg_rank": int(avg_rank),
        }

    def generate_recommendations(
        self,
        asin: str,
        price_analysis: Dict[str, Any],
        rank_analysis: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """基于竞品价格和排名信号生成建议。"""
        _ = asin
        recommendations: List[Dict[str, Any]] = []

        if price_analysis.get("trend") == "decreasing":
            recommendations.append(
                {
                    "type": "adjust_price",
                    "priority": "high",
                    "title": "竞品降价，建议跟进",
                    "description": f"竞品价格下降 {abs(price_analysis.get('change_percent', 0)):.1f}%",
                }
            )

        if rank_analysis.get("status") == "declining":
            recommendations.append(
                {
                    "type": "increase_ads",
                    "priority": "medium",
                    "title": "排名下降，建议增加广告投放",
                    "description": f"排名下降 {abs(rank_analysis.get('change', 0))} 位",
                }
            )

        return recommendations
