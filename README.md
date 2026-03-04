# Amazon Listing Automation System

亚马逊上新跟卖自动化系统 - 基于 BU2Ama 核心引擎的平台化升级

## 项目概述

本项目是一个独立的亚马逊电商运营自动化平台，实现了从选品到测试迭代的完整运营链路自动化。

### 核心功能

1. **风险预检** - 商标/IP词/禁用词扫描
2. **上架质检** - 字段完整性/图片规范/变体逻辑检查
3. **数据回流** - 广告/订单/售后数据聚合
4. **阈值预警** - CVR/退款率/拒付率异常预警
5. **自动分层** - 测试款自动评级与晋级决策
6. **竞品监控** - 价格/评论/排名变化追踪

### 与 BU2Ama 的关系

本项目复用 BU2Ama 的核心引擎：
- Excel 处理引擎（加色加码）
- 跟卖处理引擎（SKC 匹配）
- 颜色映射管理
- 导出历史管理

通过 Git Submodule 或代码复制的方式集成。

## 技术栈

### 后端
- **Python 3.11+**
- **FastAPI** - Web 框架
- **PostgreSQL** - 主数据库
- **Redis** - 缓存和任务队列
- **Celery** - 异步任务处理
- **openpyxl** - Excel 处理

### 前端
- **React 18 + TypeScript**
- **Vite** - 构建工具
- **Tailwind CSS** - 样式框架
- **React Query** - 服务器状态管理
- **Zustand** - 客户端状态管理

## 快速开始

### 方式 1：使用 Docker Compose（推荐）

```bash
# 启动所有服务
docker-compose up

# 访问
# 前端: http://localhost:5174
# 后端: http://localhost:8001
# API 文档: http://localhost:8001/docs
```

### 方式 2：本地开发

#### 后端
```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload --port 8001
```

#### 前端
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 项目结构

```
AmazonListingAutomation/
├── backend/
│   ├── app/
│   │   ├── api/              # API 路由
│   │   │   ├── compliance.py    # 合规检查 API
│   │   │   ├── listing_qa.py    # 质检 API
│   │   │   ├── workflow.py      # 工作流 API
│   │   │   ├── analytics.py     # 数据分析 API
│   │   │   └── experiment.py    # 测试分层 API
│   │   ├── core/             # 核心引擎（从 BU2Ama 复用）
│   │   │   ├── excel_processor.py
│   │   │   ├── follow_sell_processor.py
│   │   │   ├── color_mapper.py
│   │   │   └── export_history.py
│   │   ├── services/         # 领域服务
│   │   │   ├── compliance_service.py
│   │   │   ├── listing_qa_service.py
│   │   │   ├── workflow_service.py
│   │   │   ├── data_pipeline_service.py
│   │   │   ├── alert_service.py
│   │   │   └── experiment_service.py
│   │   ├── models/           # 数据模型
│   │   │   ├── compliance.py
│   │   │   ├── listing_qa.py
│   │   │   ├── workflow.py
│   │   │   └── analytics.py
│   │   ├── config.py         # 配置管理
│   │   └── main.py           # 应用入口
│   ├── migrations/           # 数据库迁移
│   ├── tests/                # 测试
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/       # React 组件
│   │   ├── services/         # API 服务
│   │   ├── store/            # 状态管理
│   │   ├── types/            # TypeScript 类型
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
├── data/                     # 数据文件
├── uploads/                  # 上传文件
├── templates/                # Excel 模板
├── docs/                     # 文档
│   ├── plans/                # 实施计划
│   └── api/                  # API 文档
├── docker-compose.yml
├── .gitignore
└── README.md
```

## 开发阶段

### P0 阶段（4-6周）- 风险预检与质检
- [x] 项目初始化
- [ ] 数据库表结构设计
- [ ] 合规检查服务
- [ ] 上架质检服务
- [ ] 审批闸门

### P1 阶段（4-8周）- 数据回流与预警
- [ ] 投放数据回流
- [ ] 阈值预警系统
- [ ] 指标看板

### P2 阶段（6-10周）- 自动化决策
- [ ] 自动分层引擎
- [ ] 竞品监控
- [ ] 智能建议

## 从 BU2Ama 复用代码

### 方式 1：Git Submodule（推荐）
```bash
# 添加 BU2Ama 为 submodule
git submodule add ../BU2Ama backend/bu2ama

# 在代码中引用
from bu2ama.app.core.excel_processor import excel_processor
```

### 方式 2：直接复制
```bash
# 复制核心模块
cp -r ../BU2Ama/backend/app/core/* backend/app/core/
cp -r ../BU2Ama/data/* data/
cp -r ../BU2Ama/templates/* templates/
```

### 方式 3：Python Package
```bash
# 将 BU2Ama 打包为 Python 包
cd ../BU2Ama/backend
pip install -e .

# 在新项目中安装
pip install -e ../BU2Ama/backend
```

## 配置说明

### 环境变量
```bash
# .env
DATABASE_URL=postgresql://user:password@localhost:5432/amazon_listing
REDIS_URL=redis://localhost:6379/0
CORS_ORIGINS=http://localhost:5174

# BU2Ama 核心引擎路径
BU2AMA_CORE_PATH=../BU2Ama/backend/app/core
BU2AMA_DATA_PATH=../BU2Ama/data
BU2AMA_TEMPLATES_PATH=../BU2Ama/templates
```

### 数据库配置
```bash
# 创建数据库
createdb amazon_listing

# 运行迁移
alembic upgrade head
```

## API 文档

启动服务后访问：http://localhost:8001/docs

### 主要 API 端点

#### 合规检查
- `POST /api/compliance/check` - 执行合规检查
- `GET /api/compliance/rules` - 获取规则列表

#### 质检
- `POST /api/listing-qa/check` - 执行质检
- `GET /api/listing-qa/checkpoints` - 获取检查点配置

#### 工作流
- `POST /api/workflow/run` - 执行工作流
- `GET /api/workflow/status/{job_id}` - 查询任务状态

#### 数据分析
- `GET /api/analytics/dashboard` - 获取看板数据
- `GET /api/analytics/alerts` - 获取预警列表

## 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/services/test_compliance_service.py

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

## 部署

### Docker 部署
```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 生产环境
```bash
# 使用生产配置
docker-compose -f docker-compose.prod.yml up -d
```

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

MIT License

## 联系方式

- 项目负责人: Melody Lu
- 邮箱: [your-email]
- 项目链接: https://github.com/yourusername/AmazonListingAutomation

## 相关文档

- [实施方案](docs/亚马逊上新跟卖系统实施方案.md)
- [P0 阶段开发计划](docs/plans/2026-03-04-amazon-listing-automation-phase0.md)
- [API 文档](http://localhost:8001/docs)
- [BU2Ama 项目](../BU2Ama)

## 更新日志

### v0.1.0 (2026-03-04)
- 项目初始化
- 基础架构搭建
- 从 BU2Ama 复用核心引擎
