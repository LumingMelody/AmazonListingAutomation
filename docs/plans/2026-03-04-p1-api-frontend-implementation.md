# P1 阶段：API 端点和前端集成实施计划

> **For Codex:** 使用 TDD 流程实现 API 端点和前端组件

**Goal:** 完成数据导入 API、预警 API 和监控看板前端

**Architecture:** RESTful API + React 监控看板

**Tech Stack:** FastAPI, React 18, React Query, Recharts

---

## Task 4: 数据导入 API 端点

**Files:**
- Create: `backend/app/api/analytics.py`
- Create: `backend/tests/test_analytics_api.py`

**Step 1: 编写 API 测试**

```python
# backend/tests/test_analytics_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_import_ad_performance_endpoint():
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
                    "date": "2026-03-01"
                }
            ]
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["imported"] == 1

def test_import_listing_metrics_endpoint():
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
                    "date": "2026-03-01"
                }
            ]
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["imported"] == 1

def test_get_metrics_summary():
    """测试获取指标汇总"""
    response = client.get("/api/analytics/metrics/summary?days=7")

    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "data" in data
```

**Step 2: 实现 API 端点**

```python
# backend/app/api/analytics.py
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import date, timedelta

from app.core.data_import_service import DataImportService

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

data_import_service = DataImportService()

class ImportRequest(BaseModel):
    data: List[Dict[str, Any]]

@router.post("/import/ad-performance")
async def import_ad_performance(request: ImportRequest) -> Dict[str, Any]:
    """导入广告表现数据"""
    try:
        result = data_import_service.import_ad_performance(request.data)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@router.post("/import/listing-metrics")
async def import_listing_metrics(request: ImportRequest) -> Dict[str, Any]:
    """导入 Listing 指标数据"""
    try:
        result = data_import_service.import_listing_metrics(request.data)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@router.get("/metrics/summary")
async def get_metrics_summary(days: int = Query(7, ge=1, le=90)) -> Dict[str, Any]:
    """获取指标汇总"""
    try:
        # TODO: 实现实际的数据查询逻辑
        return {
            "success": True,
            "data": {
                "period": f"last_{days}_days",
                "total_sessions": 0,
                "total_orders": 0,
                "total_sales": 0.0,
                "avg_cvr": 0.0
            }
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
```

**Step 3: 注册路由到 main.py**

```python
# backend/app/main.py
from app.api import analytics

app.include_router(analytics.router)
```

**Step 4: Commit**

```bash
git add backend/app/api/analytics.py backend/tests/test_analytics_api.py backend/app/main.py
git commit -m "feat(p1): add analytics API endpoints for data import"
```

---

## Task 5: 预警 API 端点

**Files:**
- Create: `backend/app/api/alerts.py`
- Create: `backend/tests/test_alerts_api.py`

**Step 1: 编写 API 测试**

```python
# backend/tests/test_alerts_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_check_metrics_endpoint():
    """测试指标检查接口"""
    response = client.post(
        "/api/alerts/check",
        json={
            "metrics": {
                "asin": "B001",
                "sessions": 1000,
                "units_ordered": 5,
                "cvr": 0.005
            }
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "alerts" in data
    assert isinstance(data["alerts"], list)

def test_get_active_alerts():
    """测试获取活跃预警"""
    response = client.get("/api/alerts/active")

    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "alerts" in data

def test_resolve_alert():
    """测试解决预警"""
    response = client.post(
        "/api/alerts/1/resolve",
        json={"reason": "已处理"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
```

**Step 2: 实现 API 端点**

```python
# backend/app/api/alerts.py
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel

from app.core.alert_service import AlertService

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

alert_service = AlertService()

class CheckMetricsRequest(BaseModel):
    metrics: Dict[str, Any]

class ResolveAlertRequest(BaseModel):
    reason: str

@router.post("/check")
async def check_metrics(request: CheckMetricsRequest) -> Dict[str, Any]:
    """检查指标并生成预警"""
    try:
        alerts = alert_service.check_metrics(request.metrics)
        return {"alerts": alerts}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@router.get("/active")
async def get_active_alerts() -> Dict[str, Any]:
    """获取活跃预警列表"""
    try:
        # TODO: 从数据库查询活跃预警
        return {
            "success": True,
            "alerts": []
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@router.post("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int = Path(..., ge=1),
    request: ResolveAlertRequest = None
) -> Dict[str, Any]:
    """解决预警"""
    try:
        # TODO: 更新数据库中的预警状态
        return {
            "success": True,
            "message": f"Alert {alert_id} resolved"
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
```

**Step 3: 注册路由**

```python
# backend/app/main.py
from app.api import alerts

app.include_router(alerts.router)
```

**Step 4: Commit**

```bash
git add backend/app/api/alerts.py backend/tests/test_alerts_api.py backend/app/main.py
git commit -m "feat(p1): add alerts API endpoints"
```

---

## Task 6: 监控看板前端组件

**Files:**
- Create: `frontend/src/components/MetricCard.tsx`
- Create: `frontend/src/components/AlertList.tsx`
- Create: `frontend/src/pages/Dashboard.tsx`

**Step 1: 创建指标卡片组件**

```typescript
// frontend/src/components/MetricCard.tsx
interface MetricCardProps {
  title: string
  value: string | number
  change?: number
  trend?: 'up' | 'down' | 'neutral'
}

export function MetricCard({ title, value, change, trend }: MetricCardProps) {
  const trendColor = trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-gray-600'

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6">
      <h3 className="text-sm font-medium text-slate-600">{title}</h3>
      <div className="mt-2 flex items-baseline">
        <p className="text-3xl font-semibold text-slate-900">{value}</p>
        {change !== undefined && (
          <span className={`ml-2 text-sm ${trendColor}`}>
            {change > 0 ? '+' : ''}{change}%
          </span>
        )}
      </div>
    </div>
  )
}
```

**Step 2: 创建预警列表组件**

```typescript
// frontend/src/components/AlertList.tsx
import { useState, useEffect } from 'react'

interface Alert {
  id: number
  type: string
  severity: string
  message: string
  asin?: string
  created_at: string
}

export function AlertList() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAlerts()
  }, [])

  const fetchAlerts = async () => {
    try {
      const response = await fetch('/api/alerts/active')
      const data = await response.json()
      setAlerts(data.alerts || [])
    } catch (error) {
      console.error('Failed to fetch alerts:', error)
    } finally {
      setLoading(false)
    }
  }

  const resolveAlert = async (alertId: number) => {
    try {
      await fetch(`/api/alerts/${alertId}/resolve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason: '已处理' })
      })
      fetchAlerts()
    } catch (error) {
      console.error('Failed to resolve alert:', error)
    }
  }

  if (loading) {
    return <div className="text-center py-8">加载中...</div>
  }

  if (alerts.length === 0) {
    return (
      <div className="rounded-lg border border-slate-200 bg-white p-8 text-center">
        <p className="text-slate-600">暂无活跃预警</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {alerts.map((alert) => (
        <div
          key={alert.id}
          className="rounded-lg border border-slate-200 bg-white p-4 flex items-start justify-between"
        >
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <span className={`px-2 py-1 text-xs rounded ${
                alert.severity === 'critical' ? 'bg-red-100 text-red-800' :
                alert.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                'bg-yellow-100 text-yellow-800'
              }`}>
                {alert.severity}
              </span>
              {alert.asin && (
                <span className="text-sm text-slate-600">ASIN: {alert.asin}</span>
              )}
            </div>
            <p className="mt-2 text-sm text-slate-900">{alert.message}</p>
            <p className="mt-1 text-xs text-slate-500">{alert.created_at}</p>
          </div>
          <button
            onClick={() => resolveAlert(alert.id)}
            className="ml-4 px-3 py-1 text-sm text-slate-600 hover:text-slate-900"
          >
            解决
          </button>
        </div>
      ))}
    </div>
  )
}
```

**Step 3: 创建监控看板页面**

```typescript
// frontend/src/pages/Dashboard.tsx
import { useState, useEffect } from 'react'
import { MetricCard } from '@/components/MetricCard'
import { AlertList } from '@/components/AlertList'

export function Dashboard() {
  const [metrics, setMetrics] = useState({
    total_sessions: 0,
    total_orders: 0,
    total_sales: 0,
    avg_cvr: 0
  })

  useEffect(() => {
    fetchMetrics()
  }, [])

  const fetchMetrics = async () => {
    try {
      const response = await fetch('/api/analytics/metrics/summary?days=7')
      const data = await response.json()
      if (data.success) {
        setMetrics(data.data)
      }
    } catch (error) {
      console.error('Failed to fetch metrics:', error)
    }
  }

  return (
    <div className="min-h-screen bg-slate-100 py-8">
      <div className="mx-auto max-w-7xl px-6">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900">数据监控看板</h1>
          <p className="mt-2 text-slate-600">P1: 数据回流与预警</p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricCard
            title="总会话数"
            value={metrics.total_sessions.toLocaleString()}
            change={5.2}
            trend="up"
          />
          <MetricCard
            title="总订单数"
            value={metrics.total_orders.toLocaleString()}
            change={-2.1}
            trend="down"
          />
          <MetricCard
            title="总销售额"
            value={`$${metrics.total_sales.toLocaleString()}`}
            change={8.3}
            trend="up"
          />
          <MetricCard
            title="平均转化率"
            value={`${(metrics.avg_cvr * 100).toFixed(2)}%`}
            change={0}
            trend="neutral"
          />
        </div>

        <div>
          <h2 className="text-xl font-semibold text-slate-900 mb-4">活跃预警</h2>
          <AlertList />
        </div>
      </div>
    </div>
  )
}
```

**Step 4: 更新 App.tsx**

```typescript
// frontend/src/App.tsx
import { Dashboard } from '@/pages/Dashboard'
import { ExcelProcessor } from '@/pages/ExcelProcessor'
import { useState } from 'react'

function App() {
  const [currentPage, setCurrentPage] = useState<'dashboard' | 'processor'>('dashboard')

  return (
    <div className="min-h-screen bg-slate-100">
      <nav className="bg-white border-b border-slate-200">
        <div className="mx-auto max-w-7xl px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-bold text-slate-900">Amazon Listing Automation</h1>
            <div className="flex gap-4">
              <button
                onClick={() => setCurrentPage('dashboard')}
                className={`px-4 py-2 rounded ${
                  currentPage === 'dashboard'
                    ? 'bg-slate-900 text-white'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                监控看板
              </button>
              <button
                onClick={() => setCurrentPage('processor')}
                className={`px-4 py-2 rounded ${
                  currentPage === 'processor'
                    ? 'bg-slate-900 text-white'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Excel 处理
              </button>
            </div>
          </div>
        </div>
      </nav>

      {currentPage === 'dashboard' ? <Dashboard /> : <ExcelProcessor />}
    </div>
  )
}

export default App
```

**Step 5: Commit**

```bash
git add frontend/src/components/MetricCard.tsx frontend/src/components/AlertList.tsx frontend/src/pages/Dashboard.tsx frontend/src/App.tsx
git commit -m "feat(p1): add monitoring dashboard with metrics and alerts"
```

---

## 执行策略

将 Task 4-6 分配给 3 个并行的 Codex 会话：
- **Codex 1**: Task 4 (数据导入 API)
- **Codex 2**: Task 5 (预警 API)
- **Codex 3**: Task 6 (监控看板前端)
