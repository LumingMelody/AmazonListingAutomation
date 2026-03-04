# P2 阶段：自动分层与竞品监控实施计划

> **For Codex:** 使用 TDD 流程实现自动分层引擎和竞品监控功能

**Goal:** 实现测试款自动评级、晋级决策和竞品监控系统

**Architecture:** 评级引擎 + 决策引擎 + 爬虫系统 + 建议生成器

**Tech Stack:** FastAPI, PostgreSQL, Celery, Redis, React Query

---

## 阶段概览

### P2 核心功能
- **自动分层引擎**: 测试款评级算法、淘汰/观察/放量判定
- **竞品监控**: 价格变化追踪、评论数量监控、排名波动预警
- **智能建议**: 加色加码时机推荐、价格调整建议、库存补货提醒

---

## Task 1: 数据库表结构（自动分层）

**Files:**
- Create: `backend/migrations/003_experiment_tables.sql`
- Create: `backend/app/models/experiment.py`

**数据库表设计:**

```sql
-- 测试配置表
CREATE TABLE IF NOT EXISTS experiment_configs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    min_sample_size INTEGER DEFAULT 100,
    cvr_threshold DECIMAL(5,4),
    refund_rate_threshold DECIMAL(5,4),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Listing 生命周期表
CREATE TABLE IF NOT EXISTS listing_lifecycle (
    id SERIAL PRIMARY KEY,
    asin VARCHAR(20) NOT NULL,
    sku VARCHAR(50),
    status VARCHAR(20) NOT NULL,
    stage VARCHAR(20) NOT NULL,
    score DECIMAL(5,2),
    sessions_total INTEGER DEFAULT 0,
    orders_total INTEGER DEFAULT 0,
    cvr DECIMAL(5,4),
    refund_rate DECIMAL(5,4),
    test_start_date DATE,
    test_end_date DATE,
    decision VARCHAR(20),
    decision_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_asin (asin),
    INDEX idx_status (status),
    INDEX idx_stage (stage)
);

-- 竞品快照表
CREATE TABLE IF NOT EXISTS competitor_snapshots (
    id SERIAL PRIMARY KEY,
    asin VARCHAR(20) NOT NULL,
    competitor_asin VARCHAR(20) NOT NULL,
    price DECIMAL(10,2),
    rating DECIMAL(3,2),
    review_count INTEGER,
    rank INTEGER,
    availability VARCHAR(50),
    snapshot_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_asin_date (asin, snapshot_date),
    INDEX idx_competitor (competitor_asin)
);

-- 动作建议表
CREATE TABLE IF NOT EXISTS action_recommendations (
    id SERIAL PRIMARY KEY,
    asin VARCHAR(20) NOT NULL,
    sku VARCHAR(50),
    recommendation_type VARCHAR(50) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    data JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    executed_at TIMESTAMP,
    INDEX idx_asin_status (asin, status),
    INDEX idx_type (recommendation_type)
);
```

**Pydantic 模型:**

```python
# backend/app/models/experiment.py
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from decimal import Decimal

class ExperimentConfig(BaseModel):
    id: Optional[int] = None
    name: str
    category: Optional[str] = None
    min_sample_size: int = 100
    cvr_threshold: Optional[Decimal] = None
    refund_rate_threshold: Optional[Decimal] = None
    active: bool = True
    created_at: Optional[datetime] = None

class ListingLifecycle(BaseModel):
    id: Optional[int] = None
    asin: str
    sku: Optional[str] = None
    status: str  # testing, active, paused, discontinued
    stage: str  # test, observe, scale, eliminate
    score: Optional[Decimal] = None
    sessions_total: int = 0
    orders_total: int = 0
    cvr: Optional[Decimal] = None
    refund_rate: Optional[Decimal] = None
    test_start_date: Optional[date] = None
    test_end_date: Optional[date] = None
    decision: Optional[str] = None
    decision_reason: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class CompetitorSnapshot(BaseModel):
    id: Optional[int] = None
    asin: str
    competitor_asin: str
    price: Optional[Decimal] = None
    rating: Optional[Decimal] = None
    review_count: Optional[int] = None
    rank: Optional[int] = None
    availability: Optional[str] = None
    snapshot_date: date
    created_at: Optional[datetime] = None

class ActionRecommendation(BaseModel):
    id: Optional[int] = None
    asin: str
    sku: Optional[str] = None
    recommendation_type: str  # add_variant, adjust_price, restock, pause, scale
    priority: str  # high, medium, low
    title: str
    description: Optional[str] = None
    data: Optional[dict] = None
    status: str = "pending"  # pending, executed, dismissed
    created_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None
```

---

## Task 2: 自动分层引擎服务

**Files:**
- Create: `backend/app/core/experiment_service.py`
- Create: `backend/tests/test_experiment_service.py`

**核心功能:**

```python
# backend/app/core/experiment_service.py
from typing import Dict, Any, List
from decimal import Decimal

class ExperimentService:
    """测试款自动分层服务"""

    # 阈值配置
    THRESHOLDS = {
        "min_sessions": 100,
        "min_orders": 10,
        "cvr_min": Decimal("0.01"),  # 1%
        "cvr_good": Decimal("0.03"),  # 3%
        "refund_rate_max": Decimal("0.10"),  # 10%
        "score_eliminate": Decimal("40.0"),
        "score_observe": Decimal("60.0"),
        "score_scale": Decimal("80.0")
    }

    def evaluate_listing(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """评估 Listing 并生成决策"""

        # 1. 检查样本量
        if not self._has_sufficient_sample(metrics):
            return {
                "decision": "continue_test",
                "stage": "test",
                "score": 0,
                "reason": "样本量不足，继续测试"
            }

        # 2. 计算综合得分
        score = self._calculate_score(metrics)

        # 3. 判定阶段
        stage = self._determine_stage(score, metrics)

        # 4. 生成决策
        decision = self._make_decision(stage, metrics)

        return {
            "decision": decision,
            "stage": stage,
            "score": float(score),
            "reason": self._generate_reason(decision, stage, metrics)
        }

    def _has_sufficient_sample(self, metrics: Dict[str, Any]) -> bool:
        """检查样本量是否充足"""
        return (
            metrics.get("sessions", 0) >= self.THRESHOLDS["min_sessions"] and
            metrics.get("orders", 0) >= self.THRESHOLDS["min_orders"]
        )

    def _calculate_score(self, metrics: Dict[str, Any]) -> Decimal:
        """计算综合得分 (0-100)"""
        score = Decimal("0")

        # CVR 得分 (40分)
        cvr = Decimal(str(metrics.get("cvr", 0)))
        if cvr >= self.THRESHOLDS["cvr_good"]:
            score += Decimal("40")
        elif cvr >= self.THRESHOLDS["cvr_min"]:
            score += Decimal("20")

        # 退款率得分 (30分)
        refund_rate = Decimal(str(metrics.get("refund_rate", 0)))
        if refund_rate <= self.THRESHOLDS["refund_rate_max"]:
            score += Decimal("30")

        # 销售额得分 (30分)
        sales = Decimal(str(metrics.get("sales", 0)))
        if sales > 1000:
            score += Decimal("30")
        elif sales > 500:
            score += Decimal("15")

        return score

    def _determine_stage(self, score: Decimal, metrics: Dict[str, Any]) -> str:
        """判定阶段"""
        if score >= self.THRESHOLDS["score_scale"]:
            return "scale"
        elif score >= self.THRESHOLDS["score_observe"]:
            return "observe"
        elif score >= self.THRESHOLDS["score_eliminate"]:
            return "test"
        else:
            return "eliminate"

    def _make_decision(self, stage: str, metrics: Dict[str, Any]) -> str:
        """生成决策"""
        decisions = {
            "scale": "add_variants",  # 加色加码
            "observe": "continue_monitor",  # 继续观察
            "test": "continue_test",  # 继续测试
            "eliminate": "discontinue"  # 下架淘汰
        }
        return decisions.get(stage, "continue_test")

    def _generate_reason(self, decision: str, stage: str, metrics: Dict[str, Any]) -> str:
        """生成决策原因"""
        reasons = {
            "add_variants": f"表现优秀（CVR: {metrics.get('cvr', 0):.2%}），建议加色加码",
            "continue_monitor": "表现良好，继续观察数据",
            "continue_test": "样本量充足，继续测试",
            "discontinue": f"表现不佳（CVR: {metrics.get('cvr', 0):.2%}），建议下架"
        }
        return reasons.get(decision, "继续测试")
```

**测试用例:**

```python
# backend/tests/test_experiment_service.py
import pytest
from decimal import Decimal
from app.core.experiment_service import ExperimentService

@pytest.fixture
def experiment_service():
    return ExperimentService()

def test_evaluate_listing_insufficient_sample(experiment_service):
    """测试样本量不足的情况"""
    metrics = {
        "sessions": 50,
        "orders": 3,
        "cvr": 0.06,
        "refund_rate": 0.05,
        "sales": 150
    }

    result = experiment_service.evaluate_listing(metrics)
    assert result["decision"] == "continue_test"
    assert result["stage"] == "test"

def test_evaluate_listing_excellent_performance(experiment_service):
    """测试优秀表现"""
    metrics = {
        "sessions": 1000,
        "orders": 50,
        "cvr": 0.05,
        "refund_rate": 0.03,
        "sales": 1500
    }

    result = experiment_service.evaluate_listing(metrics)
    assert result["decision"] == "add_variants"
    assert result["stage"] == "scale"
    assert result["score"] >= 80

def test_evaluate_listing_poor_performance(experiment_service):
    """测试差劲表现"""
    metrics = {
        "sessions": 1000,
        "orders": 10,
        "cvr": 0.005,
        "refund_rate": 0.15,
        "sales": 200
    }

    result = experiment_service.evaluate_listing(metrics)
    assert result["decision"] == "discontinue"
    assert result["stage"] == "eliminate"
    assert result["score"] < 40
```

---

## Task 3: 竞品监控服务

**Files:**
- Create: `backend/app/core/competitor_monitor_service.py`
- Create: `backend/tests/test_competitor_monitor_service.py`

**核心功能:**

```python
# backend/app/core/competitor_monitor_service.py
from typing import List, Dict, Any
from decimal import Decimal
from datetime import date, timedelta

class CompetitorMonitorService:
    """竞品监控服务"""

    def analyze_price_changes(
        self,
        asin: str,
        current_price: Decimal,
        historical_prices: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """分析价格变化"""

        if not historical_prices:
            return {"trend": "stable", "change_percent": 0}

        # 计算7天平均价格
        recent_prices = [
            Decimal(str(p["price"]))
            for p in historical_prices[-7:]
            if p.get("price")
        ]

        if not recent_prices:
            return {"trend": "stable", "change_percent": 0}

        avg_price = sum(recent_prices) / len(recent_prices)
        change_percent = ((current_price - avg_price) / avg_price) * 100

        # 判定趋势
        if change_percent > 5:
            trend = "increasing"
        elif change_percent < -5:
            trend = "decreasing"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "change_percent": float(change_percent),
            "avg_price": float(avg_price),
            "current_price": float(current_price)
        }

    def detect_rank_changes(
        self,
        current_rank: int,
        historical_ranks: List[int]
    ) -> Dict[str, Any]:
        """检测排名变化"""

        if not historical_ranks:
            return {"status": "new", "change": 0}

        avg_rank = sum(historical_ranks[-7:]) / len(historical_ranks[-7:])
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
            "avg_rank": int(avg_rank)
        }

    def generate_recommendations(
        self,
        asin: str,
        price_analysis: Dict[str, Any],
        rank_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """生成竞品建议"""
        recommendations = []

        # 价格建议
        if price_analysis["trend"] == "decreasing":
            recommendations.append({
                "type": "adjust_price",
                "priority": "high",
                "title": "竞品降价，建议跟进",
                "description": f"竞品价格下降 {abs(price_analysis['change_percent']):.1f}%"
            })

        # 排名建议
        if rank_analysis["status"] == "declining":
            recommendations.append({
                "type": "increase_ads",
                "priority": "medium",
                "title": "排名下降，建议增加广告投放",
                "description": f"排名下降 {abs(rank_analysis['change'])} 位"
            })

        return recommendations
```

---

## 执行策略

使用 3 个并行 Codex 会话：
- **Codex 1**: Task 1 - 数据库表结构和模型
- **Codex 2**: Task 2 - 自动分层引擎服务
- **Codex 3**: Task 3 - 竞品监控服务
