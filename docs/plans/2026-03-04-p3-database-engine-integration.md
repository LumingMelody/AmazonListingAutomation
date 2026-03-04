# P3 阶段：数据库与 BU2Ama 核心引擎集成实施计划

> **For Codex:** 使用 TDD 流程（RED -> GREEN -> REFACTOR）完成基础设施集成，禁止先写实现后补测试。

**Goal:** 将当前内存/占位实现升级为可持久化、可迁移、可扩展的生产级后端基础设施。  
**Architecture:** PostgreSQL + Alembic + SQLAlchemy（数据层）+ BU2Ama Adapter Layer（引擎适配层）。  
**Tech Stack:** FastAPI, PostgreSQL 15, SQLAlchemy 2.x, Alembic, pytest。

---

## 阶段范围

### In Scope
- 数据库访问统一到 SQLAlchemy Session。
- 使用 Alembic 管理 schema 版本，不再手工执行分散 SQL。
- 引入 BU2Ama 服务适配层，屏蔽外部引擎差异。
- API 层通过依赖注入调用 Adapter，不直接耦合 BU2Ama 文件结构。

### Out of Scope
- 新增业务策略（如新的评分算法）。
- 前端改造。
- 分布式任务编排优化（Celery 深度改造）。

---

## Task 1: 数据库集成（PostgreSQL + Alembic + SQLAlchemy）

**Files:**
- Create: `backend/app/db/base.py`
- Create: `backend/app/db/session.py`
- Create: `backend/app/db/models/compliance.py`
- Create: `backend/app/db/models/analytics.py`
- Create: `backend/app/db/models/experiment.py`
- Create: `backend/alembic.ini`
- Create: `backend/migrations/env.py`
- Create: `backend/migrations/versions/20260304_01_init_schema.py`
- Update: `backend/app/config.py`
- Update: `backend/app/main.py`
- Create: `backend/tests/test_db_session.py`
- Create: `backend/tests/test_alembic_migration.py`
- Create: `backend/tests/test_health_db_integration.py`

### Step 1 (RED): 先写数据库基础失败测试

```python
# backend/tests/test_db_session.py
from sqlalchemy import text

from app.db.session import SessionLocal


def test_session_can_execute_simple_query() -> None:
    with SessionLocal() as session:
        value = session.execute(text("SELECT 1")).scalar_one()
    assert value == 1
```

```python
# backend/tests/test_health_db_integration.py
from fastapi.testclient import TestClient
from app.main import app


def test_health_endpoint_returns_real_db_status() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["database"] in {"connected", "disconnected"}
    assert isinstance(payload.get("database_error"), (str, type(None)))
```

预期：当前实现会失败或不满足断言（`/health` 还在硬编码 `connected`）。

### Step 2 (GREEN): 建立 SQLAlchemy 基础设施

```python
# backend/app/db/base.py
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
```

```python
# backend/app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Step 3 (RED -> GREEN): 迁移测试先行，再落地 Alembic

```python
# backend/tests/test_alembic_migration.py
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


def test_upgrade_head_creates_core_tables(tmp_path) -> None:
    cfg = Config("alembic.ini")
    command.upgrade(cfg, "head")

    engine = create_engine(cfg.get_main_option("sqlalchemy.url"))
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())

    assert "compliance_rules" in tables
    assert "listing_metrics" in tables
    assert "listing_lifecycle" in tables
```

```python
# backend/migrations/env.py (关键片段)
from app.db.base import Base
from app.db.models import compliance, analytics, experiment  # noqa: F401

target_metadata = Base.metadata
```

```python
# backend/migrations/versions/20260304_01_init_schema.py (关键片段)
def upgrade() -> None:
    op.create_table(...)
    op.create_index(...)


def downgrade() -> None:
    op.drop_table(...)
```

### Step 4 (GREEN): ORM 模型落地并与现有 Pydantic 模型解耦

```python
# backend/app/db/models/compliance.py
from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ComplianceRuleORM(Base):
    __tablename__ = "compliance_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False)
    pattern: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    action: Mapped[str] = mapped_column(String(20), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())
```

建议分层：
- `app/db/models/*`：ORM 持久化模型。
- `app/models/*`：Pydantic API 模型（DTO）。

### Step 5 (REFACTOR): 应用启动与健康检查改为真实 DB 探测

```python
# backend/app/main.py (健康检查关键逻辑)
from sqlalchemy import text
from app.db.session import engine

@app.get("/health")
async def health_check():
    db_status = "connected"
    db_error = None
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        db_status = "disconnected"
        db_error = str(exc)

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "database_error": db_error,
        "redis": "connected"
    }
```

### Step 6: 测试与验收命令

```bash
# 1) RED
pytest tests/test_db_session.py tests/test_alembic_migration.py tests/test_health_db_integration.py -q

# 2) GREEN（实现后）
alembic upgrade head
pytest tests/test_db_session.py tests/test_alembic_migration.py tests/test_health_db_integration.py -q

# 3) 全量回归
pytest -q
```

**Task 1 测试用例清单：**
- `test_session_can_execute_simple_query`
- `test_get_db_closes_session_after_request`
- `test_upgrade_head_creates_core_tables`
- `test_downgrade_base_drops_tables`（可选）
- `test_health_endpoint_returns_real_db_status`
- `test_health_endpoint_returns_degraded_when_db_down`

**Task 1 完成标准（DoD）：**
- Alembic 可执行 `upgrade head`。
- 所有核心表由 Alembic 统一创建。
- `/health` 返回真实数据库连通状态。
- 数据访问通过 `SessionLocal/get_db` 统一注入。

---

## Task 2: BU2Ama 核心引擎集成（服务适配层）

**Files:**
- Create: `backend/app/services/bu2ama/interfaces.py`
- Create: `backend/app/services/bu2ama/types.py`
- Create: `backend/app/services/bu2ama/adapters.py`
- Create: `backend/app/services/bu2ama/factory.py`
- Create: `backend/app/services/bu2ama/exceptions.py`
- Update: `backend/app/api/excel.py`
- Update: `backend/app/api/followsell.py`
- Create: `backend/tests/test_bu2ama_adapter.py`
- Create: `backend/tests/test_bu2ama_factory.py`
- Create: `backend/tests/test_excel_api_adapter_integration.py`
- Create: `backend/tests/test_followsell_api_adapter_integration.py`

### Step 1 (RED): 先写 Adapter 契约测试

```python
# backend/tests/test_bu2ama_adapter.py
from app.services.bu2ama.adapters import LocalFallbackAdapter
from app.services.bu2ama.types import ProcessRequestDTO


def test_local_adapter_returns_standardized_result() -> None:
    adapter = LocalFallbackAdapter()
    result = adapter.process_excel(ProcessRequestDTO(mode="add-color", template_type="DaMaUS", skus=["SKU1"]))

    assert result.success is True
    assert result.output_file.endswith(".xlsx")
    assert result.engine_source in {"local", "bu2ama"}
```

```python
# backend/tests/test_bu2ama_factory.py
from app.services.bu2ama.factory import build_bu2ama_adapter


def test_factory_fallback_when_bu2ama_path_missing(monkeypatch) -> None:
    monkeypatch.setenv("BU2AMA_CORE_PATH", "/not-exists")
    adapter = build_bu2ama_adapter()
    assert adapter.__class__.__name__ == "LocalFallbackAdapter"
```

### Step 2 (GREEN): 定义统一接口和 DTO

```python
# backend/app/services/bu2ama/interfaces.py
from typing import Protocol
from app.services.bu2ama.types import ProcessRequestDTO, ProcessResultDTO, FollowSellRequestDTO


class Bu2AmaAdapter(Protocol):
    def process_excel(self, req: ProcessRequestDTO) -> ProcessResultDTO: ...
    def process_followsell(self, req: FollowSellRequestDTO) -> ProcessResultDTO: ...
```

```python
# backend/app/services/bu2ama/types.py
from pydantic import BaseModel


class ProcessRequestDTO(BaseModel):
    mode: str
    template_type: str
    skus: list[str]


class FollowSellRequestDTO(BaseModel):
    old_file: str
    new_file: str


class ProcessResultDTO(BaseModel):
    success: bool
    output_file: str | None = None
    error: str | None = None
    engine_source: str
```

### Step 3 (GREEN): 实现外部引擎适配 + 本地兜底适配

```python
# backend/app/services/bu2ama/adapters.py (关键片段)
import importlib.util
from pathlib import Path

from app.services.bu2ama.types import ProcessResultDTO


class ExternalBu2AmaAdapter:
    def __init__(self, core_path: str):
        self.core_path = Path(core_path)
        if not self.core_path.exists():
            raise FileNotFoundError(core_path)

    def process_excel(self, req):
        # 动态加载 BU2Ama 核心模块并执行
        return ProcessResultDTO(success=True, output_file="bu2ama_output.xlsx", engine_source="bu2ama")


class LocalFallbackAdapter:
    def process_excel(self, req):
        return ProcessResultDTO(success=True, output_file=f"processed_{req.mode}_{req.template_type}.xlsx", engine_source="local")
```

### Step 4 (RED -> GREEN): API 集成测试先行，再替换路由调用

```python
# backend/tests/test_excel_api_adapter_integration.py
from fastapi.testclient import TestClient
from app.main import app


def test_excel_api_uses_adapter_output(monkeypatch) -> None:
    class FakeAdapter:
        def process_excel(self, req):
            return type("R", (), {"success": True, "output_file": "from_adapter.xlsx", "error": None, "engine_source": "fake"})()

    from app.api import excel
    monkeypatch.setattr(excel, "adapter", FakeAdapter())

    client = TestClient(app)
    resp = client.post("/api/process", json={"mode": "add-color", "template_type": "DaMaUS", "skus": ["SKU1"]})
    assert resp.status_code == 200
    assert resp.json()["output_file"] == "from_adapter.xlsx"
```

```python
# backend/app/api/excel.py (关键改造)
from app.services.bu2ama.factory import build_bu2ama_adapter

adapter = build_bu2ama_adapter()

@router.post("/api/process")
async def process_excel(request: ProcessRequest):
    # 保留合规预检
    # 通过 adapter 调用引擎
    result = adapter.process_excel(...)
    return {...}
```

### Step 5 (REFACTOR): 标准化错误映射和日志

```python
# backend/app/services/bu2ama/exceptions.py
class EngineNotAvailableError(RuntimeError):
    pass


class EngineExecutionError(RuntimeError):
    pass
```

建议统一错误行为：
- `EngineNotAvailableError` -> API 返回 `503`。
- `EngineExecutionError` -> API 返回 `500`，附带 request_id。
- 合规阻断仍返回 `200 + success=False`（保持当前前端契约）。

### Step 6: 测试与验收命令

```bash
# RED
pytest tests/test_bu2ama_adapter.py tests/test_bu2ama_factory.py tests/test_excel_api_adapter_integration.py tests/test_followsell_api_adapter_integration.py -q

# GREEN
pytest tests/test_bu2ama_adapter.py tests/test_bu2ama_factory.py tests/test_excel_api_adapter_integration.py tests/test_followsell_api_adapter_integration.py -q

# 回归
pytest tests/test_workflow_integration_api.py -q
```

**Task 2 测试用例清单：**
- `test_factory_loads_external_adapter_when_path_valid`
- `test_factory_fallback_when_bu2ama_path_missing`
- `test_external_adapter_normalizes_output_fields`
- `test_external_adapter_raises_engine_execution_error_on_crash`
- `test_excel_api_uses_adapter_output`
- `test_followsell_api_uses_adapter_output`
- `test_high_risk_listing_still_blocked_before_adapter_call`

**Task 2 完成标准（DoD）：**
- API 不直接依赖 BU2Ama 文件结构。
- 可通过环境变量切换 `external` / `local` 引擎。
- 适配层输出统一 DTO，前端响应结构稳定。
- 路由层集成测试通过。

---

## 执行顺序与里程碑

1. 先完成 Task 1（数据库），因为 Task 2 需要持久化作业记录与错误日志。  
2. Task 2 完成后再执行全量回归，重点覆盖 `excel/followsell/workflow`。  
3. 所有新增逻辑必须遵循单个循环：`写失败测试 -> 最小实现 -> 重构`。

---

## 建议提交拆分

```bash
# Commit 1
feat(p3): add sqlalchemy session and alembic baseline migration

# Commit 2
feat(p3): migrate health check and db integration tests

# Commit 3
feat(p3): add bu2ama adapter layer with factory and api integration

# Commit 4
test(p3): add adapter contract and integration test suites
```

---

## 风险与缓解

- 风险：BU2Ama 目录在本地/容器路径不一致。  
  缓解：Factory 先验证路径，失败自动切换 `LocalFallbackAdapter`。  
- 风险：已有 SQL 与 Alembic 初始版本冲突。  
  缓解：以 `20260304_01_init_schema` 作为唯一基线，旧 SQL 仅保留历史参考。  
- 风险：接口响应字段被适配层变更。  
  缓解：用 API 集成测试锁定响应契约。

---

## P3 完成判定

- 数据库迁移、连接、健康检查全部真实可用。  
- BU2Ama 通过 Adapter 接入，具备 fallback 能力。  
- 全部新增测试通过，且关键回归测试通过。  
- 文档与环境变量更新完成，可在本地与 Docker 复现。
