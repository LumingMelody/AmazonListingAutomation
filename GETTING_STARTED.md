# 快速开始指南

## 项目初始化完成 ✅

新项目 `AmazonListingAutomation` 已创建完成，与 `BU2Ama` 完全独立。

## 端口分配

为避免与 BU2Ama 冲突，使用了不同的端口：

| 服务 | BU2Ama | AmazonListingAutomation |
|------|--------|-------------------------|
| 前端 | 5173 | 5174 |
| 后端 | 8000 | 8001 |
| PostgreSQL | 5432 | 5433 |
| Redis | 6379 | 6380 |

## 启动步骤

### 1. 进入项目目录
```bash
cd /Users/melodylu/PycharmProjects/AmazonListingAutomation
```

### 2. 启动 Docker 服务
```bash
docker-compose up
```

### 3. 访问应用
- 前端: http://localhost:5174
- 后端: http://localhost:8001
- API 文档: http://localhost:8001/docs

## 复用 BU2Ama 核心代码

Docker Compose 已配置好挂载 BU2Ama 的核心模块（只读）：

```yaml
volumes:
  - ../BU2Ama/backend/app/core:/app/bu2ama_core:ro
  - ../BU2Ama/data:/app/bu2ama_data:ro
```

在代码中可以这样使用：

```python
# 方式 1: 直接导入（需要配置 Python path）
import sys
sys.path.append('/app/bu2ama_core')
from excel_processor import excel_processor

# 方式 2: 通过环境变量路径
import os
from pathlib import Path
bu2ama_core = Path(os.getenv('BU2AMA_CORE_PATH'))
```

## 开发流程

### 后端开发
```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 本地运行（不用 Docker）
uvicorn app.main:app --reload --port 8001
```

### 前端开发
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 本地运行（不用 Docker）
npm run dev
```

## 下一步开发任务

### 第 1 周：基础设施
- [ ] 创建数据库迁移文件
- [ ] 实现数据库连接
- [ ] 实现 Redis 连接
- [ ] 配置日志系统

### 第 2 周：合规检查
- [ ] 实现 ComplianceService
- [ ] 创建合规规则表
- [ ] 实现 Compliance API
- [ ] 前端合规检查界面

### 第 3 周：质检服务
- [ ] 实现 ListingQAService
- [ ] 创建质检配置表
- [ ] 实现 Listing QA API
- [ ] 前端质检界面

### 第 4 周：工作流集成
- [ ] 实现 WorkflowService
- [ ] 集成 BU2Ama 核心引擎
- [ ] 端到端测试
- [ ] 文档完善

## 与 BU2Ama 的关系

```
BU2Ama (端口 8000/5173)
  ├── 加色加码功能 ✅ 继续运行
  └── 跟卖功能 ✅ 继续运行

AmazonListingAutomation (端口 8001/5174)
  ├── 复用 BU2Ama 核心引擎 ✅
  ├── 新增合规检查 🚧
  ├── 新增质检服务 🚧
  └── 新增工作流编排 🚧
```

## 常见问题

### Q: 两个项目可以同时运行吗？
A: 可以！它们使用不同的端口，互不干扰。

### Q: 如何更新 BU2Ama 的核心代码？
A: 在 BU2Ama 项目中更新代码后，重启 AmazonListingAutomation 的 Docker 容器即可。

### Q: 如何调试？
A: 可以使用本地开发模式（不用 Docker），或者在 Docker 中使用 debugpy。

## 参考文档

- [实施方案](../BU2Ama/亚马逊上新跟卖系统实施方案.md)
- [P0 开发计划](../BU2Ama/docs/plans/2026-03-04-amazon-listing-automation-phase0.md)
- [BU2Ama 项目](../BU2Ama)

## Git 提交

```bash
# 初始化提交
git add .
git commit -m "feat: 初始化 Amazon Listing Automation 项目

- 基础项目结构
- Docker Compose 配置
- 后端 FastAPI 框架
- 前端 React + TypeScript
- 复用 BU2Ama 核心引擎"
```

---

**项目创建时间**: 2026-03-04
**创建者**: Melody Lu
**状态**: 初始化完成，准备开发
