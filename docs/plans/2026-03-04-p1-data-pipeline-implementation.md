# P1 阶段：数据回流与预警系统实施计划

> **For Codex:** 使用 TDD 流程实现数据回流和预警功能

**Goal:** 建立数据闭环，实现广告-订单-售后数据归因和阈值预警

**Architecture:** 数据管道 + 预警引擎 + 监控看板

**Tech Stack:** FastAPI, PostgreSQL, Redis, Celery, React Query

---

## Task 1: 数据库表结构（数据回流）

**Files:**
- Create: `backend/migrations/002_data_pipeline_tables.sql`
- Create: `backend/app/models/analytics.py`

**Step 1: 编写数据库迁移脚本**

```sql
-- 广告表现表
CREATE TABLE IF NOT EXISTS ad_performance (
    id SERIAL PRIMARY KEY,
    campaign_id VARCHAR(100) NOT NULL,
    ad_group_id VARCHAR(100),
    keyword VARCHAR(200),
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    spend DECIMAL(10,2) DEFAULT 0,
    sales DECIMAL(10,2) DEFAULT 0,
    orders INTEGER DEFAULT 0,
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_campaign_date (campaign_id, date),
    INDEX idx_date (date)
);

-- Listing 指标表
CREATE TABLE IF NOT EXISTS listing_metrics (
    id SERIAL PRIMARY KEY,
    asin VARCHAR(20) NOT NULL,
    sku VARCHAR(50),
    sessions INTEGER DEFAULT 0,
    page_views INTEGER DEFAULT 0,
    units_ordered INTEGER DEFAULT 0,
    units_ordered_b2b INTEGER DEFAULT 0,
    unit_session_percentage DECIMAL(5,2),
    ordered_product_sales DECIMAL(10,2) DEFAULT 0,
    total_order_items INTEGER DEFAULT 0,
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_asin_date (asin, date),
    INDEX idx_sku_date (sku, date)
);

-- 预警规则表
CREATE TABLE IF NOT EXISTS alert_rules (
    id SERIAL PRIMARY KEY,
    rule_name VARCHAR(100) NOT NULL,
    metric_name VARCHAR(50) NOT NULL,
    condition VARCHAR(20) NOT NULL,
    threshold_value DECIMAL(10,4) NOT NULL,
    time_window INTEGER DEFAULT 24,
    severity VARCHAR(20) NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 预警历史表
CREATE TABLE IF NOT EXISTS alert_history (
    id SERIAL PRIMARY KEY,
    rule_id INTEGER REFERENCES alert_rules(id),
    asin VARCHAR(20),
    sku VARCHAR(50),
    metric_value DECIMAL(10,4),
    threshold_value DECIMAL(10,4),
    message TEXT,
    severity VARCHAR(20),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);
```

**Step 2: 创建 Pydantic 模型**

```python
# backend/app/models/analytics.py
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from decimal import Decimal

class AdPerformance(BaseModel):
    id: Optional[int] = None
    campaign_id: str
    ad_group_id: Optional[str] = None
    keyword: Optional[str] = None
    impressions: int = 0
    clicks: int = 0
    spend: Decimal = Decimal('0')
    sales: Decimal = Decimal('0')
    orders: int = 0
    date: date
    created_at: Optional[datetime] = None

class ListingMetrics(BaseModel):
    id: Optional[int] = None
    asin: str
    sku: Optional[str] = None
    sessions: int = 0
    page_views: int = 0
    units_ordered: int = 0
    units_ordered_b2b: int = 0
    unit_session_percentage: Optional[Decimal] = None
    ordered_product_sales: Decimal = Decimal('0')
    total_order_items: int = 0
    date: date
    created_at: Optional[datetime] = None

class AlertRule(BaseModel):
    id: Optional[int] = None
    rule_name: str
    metric_name: str
    condition: str
    threshold_value: Decimal
    time_window: int = 24
    severity: str
    active: bool = True
    created_at: Optional[datetime] = None

class AlertHistory(BaseModel):
    id: Optional[int] = None
    rule_id: int
    asin: Optional[str] = None
    sku: Optional[str] = None
    metric_value: Decimal
    threshold_value: Decimal
    message: str
    severity: str
    status: str = "pending"
    created_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
```

**Step 3: Commit**

```bash
git add backend/migrations/002_data_pipeline_tables.sql backend/app/models/analytics.py
git commit -m "feat(p1): add data pipeline database schema"
```

---

## Task 2: 数据导入服务

**Files:**
- Create: `backend/app/core/data_import_service.py`
- Create: `backend/tests/test_data_import_service.py`

**Step 1: 编写测试**

```python
# backend/tests/test_data_import_service.py
import pytest
from datetime import date
from decimal import Decimal
from app.core.data_import_service import DataImportService

@pytest.fixture
def import_service():
    return DataImportService()

def test_import_ad_performance_data(import_service):
    data = [{
        "campaign_id": "CAMP001",
        "impressions": 1000,
        "clicks": 50,
        "spend": "25.50",
        "date": "2026-03-01"
    }]

    result = import_service.import_ad_performance(data)
    assert result["success"] is True
    assert result["imported"] == 1

def test_import_listing_metrics(import_service):
    data = [{
        "asin": "B001",
        "sku": "SKU001",
        "sessions": 500,
        "units_ordered": 10,
        "date": "2026-03-01"
    }]

    result = import_service.import_listing_metrics(data)
    assert result["success"] is True
    assert result["imported"] == 1
```

**Step 2: 实现服务**

```python
# backend/app/core/data_import_service.py
from typing import List, Dict, Any
from datetime import datetime, date
from decimal import Decimal

class DataImportService:
    """数据导入服务"""

    def import_ad_performance(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """导入广告表现数据"""
        imported = 0
        errors = []

        for row in data:
            try:
                # TODO: 实际实现需要数据库操作
                imported += 1
            except Exception as e:
                errors.append({"row": row, "error": str(e)})

        return {
            "success": len(errors) == 0,
            "imported": imported,
            "errors": errors
        }

    def import_listing_metrics(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """导入 Listing 指标数据"""
        imported = 0
        errors = []

        for row in data:
            try:
                # TODO: 实际实现需要数据库操作
                imported += 1
            except Exception as e:
                errors.append({"row": row, "error": str(e)})

        return {
            "success": len(errors) == 0,
            "imported": imported,
            "errors": errors
        }
```

**Step 3: Commit**

```bash
git add backend/app/core/data_import_service.py backend/tests/test_data_import_service.py
git commit -m "feat(p1): add data import service"
```

---

## Task 3: 预警引擎

**Files:**
- Create: `backend/app/core/alert_service.py`
- Create: `backend/tests/test_alert_service.py`

**Step 1: 编写测试**

```python
# backend/tests/test_alert_service.py
import pytest
from app.core.alert_service import AlertService

@pytest.fixture
def alert_service():
    return AlertService()

def test_check_cvr_drop(alert_service):
    """测试转化率下降预警"""
    metrics = {
        "asin": "B001",
        "sessions": 1000,
        "units_ordered": 5,
        "cvr": 0.005
    }

    result = alert_service.check_metrics(metrics)
    assert "cvr_drop" in [a["type"] for a in result]

def test_check_refund_rate_spike(alert_service):
    """测试退款率异常预警"""
    metrics = {
        "asin": "B001",
        "orders": 100,
        "refunds": 15,
        "refund_rate": 0.15
    }

    result = alert_service.check_metrics(metrics)
    assert "refund_rate_spike" in [a["type"] for a in result]
```

**Step 2: 实现服务**

```python
# backend/app/core/alert_service.py
from typing import Dict, Any, List

class AlertService:
    """预警服务"""

    THRESHOLDS = {
        "cvr_min": 0.01,
        "refund_rate_max": 0.10,
        "chargeback_rate_max": 0.02
    }

    def check_metrics(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检查指标并生成预警"""
        alerts = []

        # CVR 下降检查
        if "cvr" in metrics and metrics["cvr"] < self.THRESHOLDS["cvr_min"]:
            alerts.append({
                "type": "cvr_drop",
                "severity": "high",
                "message": f"转化率过低: {metrics['cvr']:.2%}",
                "asin": metrics.get("asin")
            })

        # 退款率检查
        if "refund_rate" in metrics and metrics["refund_rate"] > self.THRESHOLDS["refund_rate_max"]:
            alerts.append({
                "type": "refund_rate_spike",
                "severity": "critical",
                "message": f"退款率异常: {metrics['refund_rate']:.2%}",
                "asin": metrics.get("asin")
            })

        return alerts
```

**Step 3: Commit**

```bash
git add backend/app/core/alert_service.py backend/tests/test_alert_service.py
git commit -m "feat(p1): add alert service with threshold checking"
```

---

## 执行策略

将 Task 1-3 分配给 3 个并行的 Codex 会话：
- **Codex 1**: Task 1 (数据库表结构)
- **Codex 2**: Task 2 (数据导入服务)
- **Codex 3**: Task 3 (预警引擎)
