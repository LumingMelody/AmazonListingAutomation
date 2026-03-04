# 亚马逊跟卖系统 MVP 设计方案

## 文档信息
- **创建日期**: 2026-03-04
- **设计方案**: 方案 A - 垂直切片快速打通
- **实施周期**: 2-3 周
- **版本**: v1.0

---

## 一、设计概述

### 1.1 目标

实现一条完整的跟卖业务流程，端到端打通 P0（风险预检）+ P1（数据回流）核心功能，快速验证架构设计并交付可用的最小功能集。

### 1.2 核心业务流程

```
用户上传Excel → 解析SKU → 风险预检 → SKC匹配 → 生成新Excel → 导出 → 数据回流 → 指标监控
```

### 1.3 实施策略

采用 4 个并行开发任务：
- **Task 1**: 数据库基础 + 核心模型
- **Task 2**: 跟卖主流程
- **Task 3**: 风险预检服务
- **Task 4**: 数据回流 + 指标监控

---

## 二、系统架构

### 2.1 分层架构

```
┌─────────────────────────────────────────────────────────┐
│                    前端层 (React)                         │
│  上传界面 | 任务列表 | 风险报告 | 指标看板                  │
└─────────────────────────────────────────────────────────┘
                            ↓ HTTP/REST
┌─────────────────────────────────────────────────────────┐
│                   API 层 (FastAPI)                        │
│  /api/followsell  |  /api/compliance  |  /api/analytics  │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   服务层 (Services)                       │
│  FollowSellService | ComplianceService | AnalyticsService│
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              核心引擎层 (从 BU2Ama 复用)                   │
│  ExcelProcessor | SKCMatcher | ColorMapper               │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                 数据层 (PostgreSQL + Redis)               │
│  任务表 | 规则表 | 指标表 | 缓存                          │
└─────────────────────────────────────────────────────────┘
```

### 2.2 技术栈

**后端**:
- Python 3.11+
- FastAPI (Web 框架)
- PostgreSQL (主数据库)
- Redis (缓存和任务队列)
- Celery (异步任务)
- SQLAlchemy (ORM)
- Alembic (数据库迁移)

**前端**:
- React 18 + TypeScript
- Vite (构建工具)
- Tailwind CSS + shadcn/ui
- React Query (服务器状态)
- Zustand (客户端状态)

---

## 三、数据库设计

### 3.1 核心数据表

#### 1. 跟卖任务表 (followsell_jobs)

```sql
CREATE TABLE followsell_jobs (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(20) NOT NULL,  -- pending, processing, completed, failed
    old_file_path VARCHAR(255),
    new_product_code VARCHAR(50),
    output_file_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB  -- 存储额外参数
);
```

#### 2. 风险检查记录表 (compliance_checks)

```sql
CREATE TABLE compliance_checks (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(50) REFERENCES followsell_jobs(job_id),
    check_type VARCHAR(50),  -- trademark, ip_word, forbidden_word
    risk_level VARCHAR(20),  -- safe, warning, danger
    findings JSONB,  -- 具体发现的问题
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 3. 禁用词库表 (blacklist_keywords)

```sql
CREATE TABLE blacklist_keywords (
    id SERIAL PRIMARY KEY,
    keyword VARCHAR(100) NOT NULL,
    category VARCHAR(50),  -- trademark, ip, forbidden
    severity VARCHAR(20),  -- high, medium, low
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 4. Listing 指标表 (listing_metrics)

```sql
CREATE TABLE listing_metrics (
    id SERIAL PRIMARY KEY,
    asin VARCHAR(20),
    sku VARCHAR(50),
    date DATE NOT NULL,
    sessions INT DEFAULT 0,
    orders INT DEFAULT 0,
    cvr DECIMAL(5,4),
    refund_rate DECIMAL(5,4),
    chargeback_rate DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(asin, sku, date)
);
```

#### 5. 预警记录表 (alert_records)

```sql
CREATE TABLE alert_records (
    id SERIAL PRIMARY KEY,
    alert_type VARCHAR(50),  -- cvr_drop, refund_spike, chargeback_spike
    asin VARCHAR(20),
    sku VARCHAR(50),
    metric_value DECIMAL(10,4),
    threshold_value DECIMAL(10,4),
    severity VARCHAR(20),  -- info, warning, critical
    status VARCHAR(20),  -- new, acknowledged, resolved
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 6. 阈值规则表 (threshold_rules)

```sql
CREATE TABLE threshold_rules (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(50) NOT NULL,
    category VARCHAR(50),
    threshold_value DECIMAL(10,4),
    comparison_operator VARCHAR(10),  -- gt, lt, gte, lte
    action VARCHAR(50),  -- alert, block, review
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 3.2 索引策略

```sql
-- 任务查询优化
CREATE INDEX idx_jobs_status ON followsell_jobs(status);
CREATE INDEX idx_jobs_created ON followsell_jobs(created_at DESC);

-- 风险检查查询
CREATE INDEX idx_compliance_job ON compliance_checks(job_id);
CREATE INDEX idx_compliance_level ON compliance_checks(risk_level);

-- 指标查询优化
CREATE INDEX idx_metrics_asin_date ON listing_metrics(asin, date DESC);
CREATE INDEX idx_metrics_sku_date ON listing_metrics(sku, date DESC);

-- 预警查询
CREATE INDEX idx_alerts_status ON alert_records(status, created_at DESC);
CREATE INDEX idx_alerts_asin ON alert_records(asin);
```

---

## 四、API 接口设计

### 4.1 跟卖流程 API

#### POST /api/followsell/upload
上传老款 Excel，启动跟卖任务

**Request:**
```json
{
    "old_file": "file upload",
    "new_product_code": "12345678",
    "options": {
        "enable_compliance_check": true,
        "auto_approve": false
    }
}
```

**Response:**
```json
{
    "success": true,
    "job_id": "fs_20260304_001",
    "status": "processing",
    "message": "任务已创建"
}
```

#### GET /api/followsell/status/{job_id}
查询任务状态

**Response:**
```json
{
    "job_id": "fs_20260304_001",
    "status": "completed",
    "progress": 100,
    "compliance_result": {
        "risk_level": "warning",
        "issues_found": 2
    },
    "output_file": "/downloads/fs_20260304_001.xlsx"
}
```

#### GET /api/followsell/download/{job_id}
下载生成的 Excel

**Response:** File Download

### 4.2 风险预检 API

#### POST /api/compliance/check
执行合规检查

**Request:**
```json
{
    "text": "Nike Air Jordan 运动鞋",
    "check_types": ["trademark", "ip_word", "forbidden_word"]
}
```

**Response:**
```json
{
    "risk_level": "danger",
    "findings": [
        {
            "type": "trademark",
            "keyword": "Nike",
            "severity": "high",
            "position": 0
        }
    ],
    "recommendation": "建议修改或人工审核"
}
```

#### GET /api/compliance/keywords
获取禁用词库

**Response:**
```json
{
    "total": 1500,
    "keywords": [
        {"keyword": "Nike", "category": "trademark", "severity": "high"}
    ]
}
```

#### POST /api/compliance/keywords
添加禁用词

**Request:**
```json
{
    "keyword": "Supreme",
    "category": "trademark",
    "severity": "high"
}
```

### 4.3 数据分析 API

#### GET /api/analytics/dashboard
获取看板数据

**Response:**
```json
{
    "summary": {
        "total_listings": 1250,
        "active_alerts": 15,
        "avg_cvr": 0.0325,
        "high_risk_count": 3
    },
    "recent_alerts": [
        {
            "asin": "B08XYZ123",
            "alert_type": "cvr_drop",
            "severity": "warning",
            "created_at": "2026-03-04T10:30:00Z"
        }
    ]
}
```

#### GET /api/analytics/metrics/{asin}
获取单个 ASIN 的指标

**Response:**
```json
{
    "asin": "B08XYZ123",
    "sku": "SKU-12345",
    "metrics": [
        {
            "date": "2026-03-03",
            "sessions": 150,
            "orders": 5,
            "cvr": 0.0333,
            "refund_rate": 0.02
        }
    ]
}
```

#### GET /api/analytics/alerts
获取预警列表

**Response:**
```json
{
    "total": 15,
    "alerts": [
        {
            "id": 1,
            "alert_type": "refund_spike",
            "asin": "B08ABC456",
            "metric_value": 0.15,
            "threshold_value": 0.10,
            "severity": "critical",
            "status": "new"
        }
    ]
}
```

---

## 五、服务层设计

### 5.1 跟卖服务 (FollowSellService)

```python
class FollowSellService:
    """跟卖业务服务"""

    async def create_job(self, old_file, new_product_code, options):
        """创建跟卖任务"""
        # 1. 生成任务ID
        job_id = generate_job_id()

        # 2. 保存上传文件
        file_path = save_upload_file(old_file)

        # 3. 创建任务记录
        job = create_job_record(job_id, file_path, new_product_code)

        # 4. 如果启用合规检查，先执行预检
        if options.get('enable_compliance_check'):
            compliance_result = await compliance_service.check_file(file_path)
            if compliance_result.risk_level == 'danger':
                job.status = 'blocked'
                return job

        # 5. 提交异步任务处理
        celery_task.delay(job_id)

        return job

    async def process_job(self, job_id):
        """处理跟卖任务（异步执行）"""
        # 1. 解析 Excel
        data = excel_processor.parse(job.old_file_path)

        # 2. SKC 匹配
        matched_data = skc_matcher.match(data, job.new_product_code)

        # 3. 生成新 Excel
        output_file = excel_processor.generate(matched_data)

        # 4. 更新任务状态
        update_job_status(job_id, 'completed', output_file)

        return output_file
```

### 5.2 合规检查服务 (ComplianceService)

```python
class ComplianceService:
    """合规检查服务"""

    async def check_text(self, text, check_types):
        """检查文本合规性"""
        findings = []

        # 1. 加载禁用词库（带缓存）
        keywords = await self.get_keywords_cached(check_types)

        # 2. 执行扫描
        for keyword in keywords:
            if keyword.keyword in text:
                findings.append({
                    'type': keyword.category,
                    'keyword': keyword.keyword,
                    'severity': keyword.severity,
                    'position': text.index(keyword.keyword)
                })

        # 3. 计算风险等级
        risk_level = self.calculate_risk_level(findings)

        # 4. 记录检查结果
        await self.save_check_record(text, findings, risk_level)

        return {
            'risk_level': risk_level,
            'findings': findings
        }
```

### 5.3 分析服务 (AnalyticsService)

```python
class AnalyticsService:
    """数据分析服务"""

    async def get_dashboard_data(self):
        """获取看板数据"""
        # 1. 统计总览
        summary = await self.get_summary_stats()

        # 2. 最近预警
        recent_alerts = await self.get_recent_alerts(limit=10)

        # 3. 趋势数据
        trends = await self.get_metric_trends(days=7)

        return {
            'summary': summary,
            'recent_alerts': recent_alerts,
            'trends': trends
        }

    async def check_thresholds(self, asin, metrics):
        """检查指标阈值"""
        alerts = []

        # 1. 获取阈值规则
        rules = await self.get_active_rules()

        # 2. 逐个检查
        for rule in rules:
            metric_value = metrics.get(rule.metric_name)
            if self.violates_threshold(metric_value, rule):
                alert = await self.create_alert(asin, rule, metric_value)
                alerts.append(alert)

        return alerts
```

---

## 六、数据流设计

### 6.1 完整数据流

```
┌─────────────┐
│ 用户上传    │
│ Excel文件   │
└──────┬──────┘
       ↓
┌─────────────────────┐
│ FollowSellService   │
│ - 创建任务          │
│ - 保存文件          │
└──────┬──────────────┘
       ↓
┌─────────────────────┐
│ ComplianceService   │
│ - 扫描禁用词        │
│ - 评估风险          │
└──────┬──────────────┘
       ↓
    [风险判断]
       ↓
   高风险? ──Yes──> [阻止任务]
       │
       No
       ↓
┌─────────────────────┐
│ Celery异步任务      │
│ - Excel解析         │
│ - SKC匹配           │
│ - 生成新Excel       │
└──────┬──────────────┘
       ↓
┌─────────────────────┐
│ 任务完成            │
│ - 更新状态          │
│ - 返回下载链接      │
└─────────────────────┘

[并行流程]
┌─────────────────────┐
│ AnalyticsService    │
│ - 定时导入指标      │
│ - 检查阈值          │
│ - 生成预警          │
└─────────────────────┘
```

---

## 七、错误处理

### 7.1 异常分类

```python
class BusinessException(Exception):
    """业务异常基类"""
    pass

class FileProcessingError(BusinessException):
    """文件处理异常"""
    pass

class ComplianceViolationError(BusinessException):
    """合规违规异常"""
    pass

class ThresholdViolationError(BusinessException):
    """阈值违规异常"""
    pass
```

### 7.2 统一错误响应

```json
{
    "success": false,
    "error": {
        "code": "FILE_PROCESSING_ERROR",
        "message": "Excel 文件格式不正确",
        "details": {
            "line": 10,
            "column": "SKU"
        }
    }
}
```

### 7.3 重试机制

- 临时错误（网络超时、数据库连接失败）：自动重试 3 次
- 永久错误（文件格式错误、业务规则违反）：不重试，直接标记失败
- 重试策略：指数退避（2s, 4s, 8s）

---

## 八、测试策略

### 8.1 单元测试

- 服务层逻辑测试
- 工具函数测试
- 覆盖率目标：> 80%

### 8.2 集成测试

- API 端点测试
- 数据库操作测试
- 异步任务测试

### 8.3 端到端测试

- 完整业务流程测试
- 用户场景模拟

### 8.4 性能测试

- 并发任务处理能力
- API 响应时间
- 数据库查询性能

---

## 九、部署架构

### 9.1 开发环境

```
Docker Compose:
- PostgreSQL (端口 5432)
- Redis (端口 6379)
- Backend (端口 8001)
- Frontend (端口 5174)
- Celery Worker
```

### 9.2 生产环境（未来）

```
- 负载均衡器 (Nginx)
- 应用服务器 (多实例)
- 数据库主从复制
- Redis 集群
- Celery Worker 集群
- 对象存储 (MinIO/S3)
```

---

## 十、实施计划

### Week 1: 基础设施 + 跟卖主流程

**Task 1: 数据库基础**
- 设计并创建数据库表结构
- 编写 SQLAlchemy 模型
- 创建 Alembic 迁移脚本
- 编写数据库初始化脚本

**Task 2: 跟卖主流程**
- 实现文件上传 API
- 实现 Excel 解析逻辑
- 实现 SKC 匹配逻辑
- 实现 Excel 生成导出
- 实现任务状态管理
- 集成 Celery 异步任务

### Week 2: 风险预检 + 数据回流

**Task 3: 风险预检服务**
- 实现禁用词库管理
- 实现文本扫描引擎
- 实现风险评分算法
- 集成到跟卖流程
- 实现合规检查 API

**Task 4: 数据回流 + 指标监控**
- 实现指标数据导入
- 实现阈值检查引擎
- 实现预警生成逻辑
- 实现看板 API
- 实现简单的前端界面

### Week 3: 测试 + 优化 + 文档

- 编写单元测试和集成测试
- 性能优化和调试
- 补充 API 文档
- 编写用户手册
- 准备演示环境

---

## 十一、成功指标

### 11.1 功能指标

- ✅ 用户可以上传 Excel 并生成跟卖文件
- ✅ 系统可以自动检测禁用词并预警
- ✅ 系统可以导入指标数据并生成预警
- ✅ 用户可以查看看板和预警列表

### 11.2 性能指标

- API 响应时间 < 500ms (P95)
- 单个任务处理时间 < 30s
- 支持 10 个并发任务

### 11.3 质量指标

- 单元测试覆盖率 > 80%
- 零严重 Bug
- API 文档完整

---

## 十二、风险与应对

### 12.1 技术风险

**风险**: BU2Ama 核心引擎集成困难
**应对**: 先用简化版本实现，后续再集成

**风险**: 异步任务处理性能不足
**应对**: 使用 Redis 队列 + 多 Worker

### 12.2 进度风险

**风险**: 开发时间超出预期
**应对**: 优先保证核心流程，次要功能可延后

---

## 附录

### A. 相关文档

- [亚马逊上新跟卖流程分析报告](../../亚马逊上新跟卖流程分析报告.md)
- [亚马逊上新跟卖系统实施方案](../../亚马逊上新跟卖系统实施方案.md)

### B. 技术参考

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [Celery 文档](https://docs.celeryq.dev/)
- [React Query 文档](https://tanstack.com/query/latest)

---

**设计方案生成说明**:
本设计方案采用垂直切片策略，优先实现一条完整的业务流程，快速验证架构设计并交付可用功能。设计遵循 YAGNI 原则，避免过度设计，确保每个功能都有明确的业务价值。
