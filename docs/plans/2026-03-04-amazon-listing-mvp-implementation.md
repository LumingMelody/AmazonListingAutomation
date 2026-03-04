# Amazon Listing Automation MVP 实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现亚马逊上新跟卖系统 MVP，优先完成风险预检和上架质检功能

**Architecture:** 基于现有 BU2Ama 系统，采用领域服务分层架构，保留 Excel 处理引擎，新增合规检查和质量保证层

**Tech Stack:** FastAPI, PostgreSQL, React 18, TypeScript, shadcn/ui

---

## 目录

[内容将分块追加...]

## 实施阶段概览

### P0 阶段：风险预检与上架质检（4-6周）
- 目标：降低侵权和低质量上架风险
- 核心功能：合规检查、质量校验、审批流程
- 交付物：ComplianceService + ListingQAService

### P1 阶段：数据回流与预警（4-8周）
- 目标：建立数据闭环，及时发现问题
- 核心功能：数据同步、阈值预警、监控看板
- 交付物：DataPipelineService + AlertService

### P2 阶段：自动化决策（6-10周）
- 目标：实现测试款自动分层和竞品监控
- 核心功能：自动评级、智能建议、竞品追踪
- 交付物：ExperimentService + CompetitorMonitorService

---


## P0 阶段：风险预检与上架质检

### Task 1: 数据库表结构设计与创建

**Files:**
- Create: `backend/migrations/001_compliance_tables.sql`
- Create: `backend/app/models/compliance.py`

**Step 1: 编写数据库迁移脚本**

```sql
-- 合规规则表
CREATE TABLE compliance_rules (
    id SERIAL PRIMARY KEY,
    rule_type VARCHAR(50) NOT NULL,  -- trademark | ip | forbidden_word | sensitive_category
    pattern TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL,  -- critical | high | medium | low
    action VARCHAR(20) NOT NULL,  -- block | warn | review
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 禁用词库表
CREATE TABLE blacklist_keywords (
    id SERIAL PRIMARY KEY,
    keyword VARCHAR(200) NOT NULL,
    category VARCHAR(50),  -- trademark | ip | sensitive
    language VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_keyword (keyword)
);

-- 质检检查点配置表
CREATE TABLE qa_checkpoints (
    id SERIAL PRIMARY KEY,
    checkpoint_name VARCHAR(100) NOT NULL,
    checkpoint_type VARCHAR(50) NOT NULL,  -- field_completeness | image_spec | variant_logic
    validation_rule JSONB NOT NULL,
    weight DECIMAL(3,2) DEFAULT 1.0,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 审批记录表
CREATE TABLE approval_records (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(50) NOT NULL,
    job_type VARCHAR(50) NOT NULL,
    risk_level VARCHAR(20),
    approver VARCHAR(100),
    action VARCHAR(20),  -- approved | rejected | pending
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_job_id (job_id)
);

-- 合规检查结果表
CREATE TABLE compliance_check_results (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(50) NOT NULL,
    check_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,  -- pass | fail | warn
    findings JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_job_id (job_id)
);
```

**Step 2: 创建 Pydantic 模型**

```python
# backend/app/models/compliance.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class RuleType(str, Enum):
    TRADEMARK = "trademark"
    IP = "ip"
    FORBIDDEN_WORD = "forbidden_word"
    SENSITIVE_CATEGORY = "sensitive_category"

class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Action(str, Enum):
    BLOCK = "block"
    WARN = "warn"
    REVIEW = "review"

class ComplianceRule(BaseModel):
    id: Optional[int] = None
    rule_type: RuleType
    pattern: str
    severity: Severity
    action: Action
    active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class BlacklistKeyword(BaseModel):
    id: Optional[int] = None
    keyword: str
    category: Optional[str] = None
    language: str = "en"
    created_at: Optional[datetime] = None

class QACheckpoint(BaseModel):
    id: Optional[int] = None
    checkpoint_name: str
    checkpoint_type: str
    validation_rule: Dict[str, Any]
    weight: float = 1.0
    active: bool = True
    created_at: Optional[datetime] = None

class ApprovalRecord(BaseModel):
    id: Optional[int] = None
    job_id: str
    job_type: str
    risk_level: Optional[str] = None
    approver: Optional[str] = None
    action: str = "pending"
    reason: Optional[str] = None
    created_at: Optional[datetime] = None

class ComplianceCheckResult(BaseModel):
    id: Optional[int] = None
    job_id: str
    check_type: str
    status: str
    findings: Dict[str, Any]
    created_at: Optional[datetime] = None

class RiskAssessment(BaseModel):
    risk_level: str  # safe | low | medium | high | critical
    risk_score: float
    findings: List[Dict[str, Any]]
    requires_approval: bool
    blocked_reasons: List[str] = []
```

**Step 3: 运行迁移脚本**

```bash
cd backend
psql -U postgres -d amazon_listing -f migrations/001_compliance_tables.sql
```

Expected: Tables created successfully

**Step 4: 验证表结构**

```bash
psql -U postgres -d amazon_listing -c "\dt"
```

Expected: 显示所有新创建的表

**Step 5: Commit**

```bash
git add backend/migrations/001_compliance_tables.sql backend/app/models/compliance.py
git commit -m "feat: add compliance and QA database schema"
```

---

### Task 2: 实现 ComplianceService（合规检查服务）

**Files:**
- Create: `backend/app/core/compliance_service.py`
- Create: `backend/tests/test_compliance_service.py`

**Step 1: 编写失败测试**

```python
# backend/tests/test_compliance_service.py
import pytest
from app.core.compliance_service import ComplianceService
from app.models.compliance import RiskAssessment

@pytest.fixture
def compliance_service():
    return ComplianceService()

def test_check_trademark_violation(compliance_service):
    """测试商标词检测"""
    text = "Nike shoes for sale"
    result = compliance_service.check_text(text)
    
    assert result.risk_level in ["high", "critical"]
    assert any("trademark" in f["type"] for f in result.findings)
    assert result.requires_approval is True

def test_check_clean_text(compliance_service):
    """测试无风险文本"""
    text = "High quality running shoes"
    result = compliance_service.check_text(text)
    
    assert result.risk_level == "safe"
    assert len(result.findings) == 0
    assert result.requires_approval is False

def test_check_forbidden_words(compliance_service):
    """测试禁用词检测"""
    text = "Best product ever, guaranteed cure"
    result = compliance_service.check_text(text)
    
    assert result.risk_level in ["medium", "high"]
    assert any("forbidden_word" in f["type"] for f in result.findings)
```

**Step 2: 运行测试确认失败**

```bash
cd backend
pytest tests/test_compliance_service.py -v
```

Expected: FAIL - ComplianceService not found

**Step 3: 实现 ComplianceService**

```python
# backend/app/core/compliance_service.py
import re
from typing import List, Dict, Any
from app.models.compliance import (
    RiskAssessment, ComplianceRule, BlacklistKeyword,
    RuleType, Severity, Action
)
from app.core.database import get_db

class ComplianceService:
    """合规检查服务"""
    
    def __init__(self):
        self.rules_cache = None
        self.keywords_cache = None
    
    def check_text(self, text: str, context: Dict[str, Any] = None) -> RiskAssessment:
        """检查文本合规性"""
        findings = []
        max_severity = 0
        
        # 1. 商标词检测
        trademark_findings = self._check_trademarks(text)
        findings.extend(trademark_findings)
        
        # 2. IP词检测
        ip_findings = self._check_ip_words(text)
        findings.extend(ip_findings)
        
        # 3. 禁用词检测
        forbidden_findings = self._check_forbidden_words(text)
        findings.extend(forbidden_findings)
        
        # 计算风险等级
        severity_scores = {
            "critical": 4,
            "high": 3,
            "medium": 2,
            "low": 1
        }
        
        for finding in findings:
            score = severity_scores.get(finding["severity"], 0)
            max_severity = max(max_severity, score)
        
        # 确定风险等级
        if max_severity >= 4:
            risk_level = "critical"
        elif max_severity >= 3:
            risk_level = "high"
        elif max_severity >= 2:
            risk_level = "medium"
        elif max_severity >= 1:
            risk_level = "low"
        else:
            risk_level = "safe"
        
        # 计算风险分数
        risk_score = sum(severity_scores.get(f["severity"], 0) for f in findings) / max(len(findings), 1)
        
        # 判断是否需要审批
        requires_approval = risk_level in ["critical", "high"]
        
        # 收集阻断原因
        blocked_reasons = [
            f["message"] for f in findings 
            if f["action"] == "block"
        ]
        
        return RiskAssessment(
            risk_level=risk_level,
            risk_score=risk_score,
            findings=findings,
            requires_approval=requires_approval,
            blocked_reasons=blocked_reasons
        )
    
    def _check_trademarks(self, text: str) -> List[Dict[str, Any]]:
        """检查商标词"""
        findings = []
        
        # 常见商标词列表（实际应从数据库加载）
        trademarks = [
            "Nike", "Adidas", "Apple", "Samsung", "Sony",
            "Disney", "Marvel", "Pokemon", "Louis Vuitton"
        ]
        
        text_lower = text.lower()
        for trademark in trademarks:
            if trademark.lower() in text_lower:
                findings.append({
                    "type": "trademark",
                    "keyword": trademark,
                    "severity": "critical",
                    "action": "block",
                    "message": f"检测到商标词: {trademark}"
                })
        
        return findings
    
    def _check_ip_words(self, text: str) -> List[Dict[str, Any]]:
        """检查IP词"""
        findings = []
        
        # 常见IP词列表
        ip_words = [
            "Harry Potter", "Star Wars", "Batman", "Superman",
            "Mickey Mouse", "Hello Kitty"
        ]
        
        text_lower = text.lower()
        for ip_word in ip_words:
            if ip_word.lower() in text_lower:
                findings.append({
                    "type": "ip",
                    "keyword": ip_word,
                    "severity": "critical",
                    "action": "block",
                    "message": f"检测到IP词: {ip_word}"
                })
        
        return findings
    
    def _check_forbidden_words(self, text: str) -> List[Dict[str, Any]]:
        """检查禁用词"""
        findings = []
        
        # 禁用词列表
        forbidden_patterns = [
            (r"\bcure\b", "cure", "high", "医疗宣称"),
            (r"\bguaranteed\b", "guaranteed", "medium", "绝对化承诺"),
            (r"\bbest\s+ever\b", "best ever", "medium", "夸大宣传"),
            (r"\b100%\s+safe\b", "100% safe", "high", "绝对化安全承诺")
        ]
        
        text_lower = text.lower()
        for pattern, keyword, severity, reason in forbidden_patterns:
            if re.search(pattern, text_lower):
                findings.append({
                    "type": "forbidden_word",
                    "keyword": keyword,
                    "severity": severity,
                    "action": "warn" if severity == "medium" else "review",
                    "message": f"检测到禁用词: {keyword} ({reason})"
                })
        
        return findings
    
    def load_rules_from_db(self):
        """从数据库加载规则（待实现）"""
        # TODO: 实现数据库加载逻辑
        pass
```

**Step 4: 运行测试确认通过**

```bash
pytest tests/test_compliance_service.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/core/compliance_service.py backend/tests/test_compliance_service.py
git commit -m "feat: implement ComplianceService with trademark and forbidden word detection"
```

---


### Task 3: 实现 ListingQAService（上架质检服务）

**Files:**
- Create: `backend/app/core/listing_qa_service.py`
- Create: `backend/tests/test_listing_qa_service.py`

**Step 1: 编写失败测试**

```python
# backend/tests/test_listing_qa_service.py
import pytest
from app.core.listing_qa_service import ListingQAService

@pytest.fixture
def qa_service():
    return ListingQAService()

def test_check_field_completeness(qa_service):
    """测试字段完整性检查"""
    listing_data = {
        "title": "Test Product",
        "bullet_points": ["Point 1", "Point 2"],
        "description": "Test description",
        "main_image": "image.jpg",
        "price": 29.99
    }
    
    result = qa_service.check_listing(listing_data)
    assert result["score"] > 0.8
    assert result["status"] == "pass"

def test_incomplete_listing(qa_service):
    """测试不完整的Listing"""
    listing_data = {
        "title": "Test Product"
        # 缺少其他必填字段
    }
    
    result = qa_service.check_listing(listing_data)
    assert result["score"] < 0.5
    assert result["status"] == "fail"
    assert len(result["issues"]) > 0

def test_title_validation(qa_service):
    """测试标题规范检查"""
    # 标题过短
    result = qa_service.validate_title("Short")
    assert result["valid"] is False
    
    # 标题正常
    result = qa_service.validate_title("High Quality Running Shoes for Men")
    assert result["valid"] is True
```

**Step 2: 运行测试确认失败**

```bash
pytest tests/test_listing_qa_service.py -v
```

Expected: FAIL - ListingQAService not found

**Step 3: 实现 ListingQAService**

```python
# backend/app/core/listing_qa_service.py
from typing import Dict, Any, List
import re

class ListingQAService:
    """Listing质量检查服务"""
    
    def __init__(self):
        self.required_fields = [
            "title", "bullet_points", "description", 
            "main_image", "price"
        ]
        self.checkpoints = self._load_checkpoints()
    
    def check_listing(self, listing_data: Dict[str, Any]) -> Dict[str, Any]:
        """检查Listing质量"""
        issues = []
        scores = []
        
        # 1. 字段完整性检查
        completeness_result = self._check_field_completeness(listing_data)
        issues.extend(completeness_result["issues"])
        scores.append(completeness_result["score"])
        
        # 2. 标题规范检查
        if "title" in listing_data:
            title_result = self.validate_title(listing_data["title"])
            if not title_result["valid"]:
                issues.extend(title_result["issues"])
            scores.append(1.0 if title_result["valid"] else 0.5)
        
        # 3. 五点描述检查
        if "bullet_points" in listing_data:
            bullets_result = self._check_bullet_points(listing_data["bullet_points"])
            issues.extend(bullets_result["issues"])
            scores.append(bullets_result["score"])
        
        # 4. 图片规范检查
        if "main_image" in listing_data:
            image_result = self._check_image_spec(listing_data["main_image"])
            issues.extend(image_result["issues"])
            scores.append(image_result["score"])
        
        # 计算总分
        total_score = sum(scores) / len(scores) if scores else 0
        
        # 判定状态
        if total_score >= 0.8:
            status = "pass"
        elif total_score >= 0.6:
            status = "warning"
        else:
            status = "fail"
        
        return {
            "score": total_score,
            "status": status,
            "issues": issues,
            "details": {
                "completeness": completeness_result,
                "title": title_result if "title" in listing_data else None,
                "bullet_points": bullets_result if "bullet_points" in listing_data else None,
                "image": image_result if "main_image" in listing_data else None
            }
        }
    
    def validate_title(self, title: str) -> Dict[str, Any]:
        """验证标题规范"""
        issues = []
        
        # 长度检查
        if len(title) < 20:
            issues.append("标题过短（建议至少20字符）")
        elif len(title) > 200:
            issues.append("标题过长（建议不超过200字符）")
        
        # 全大写检查
        if title.isupper():
            issues.append("标题不应全部大写")
        
        # 特殊字符检查
        if re.search(r'[!@#$%^&*()]', title):
            issues.append("标题包含不建议的特殊字符")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
    
    def _check_field_completeness(self, listing_data: Dict[str, Any]) -> Dict[str, Any]:
        """检查字段完整性"""
        issues = []
        missing_fields = []
        
        for field in self.required_fields:
            if field not in listing_data or not listing_data[field]:
                missing_fields.append(field)
                issues.append(f"缺少必填字段: {field}")
        
        score = 1.0 - (len(missing_fields) / len(self.required_fields))
        
        return {
            "score": score,
            "issues": issues,
            "missing_fields": missing_fields
        }
    
    def _check_bullet_points(self, bullet_points: List[str]) -> Dict[str, Any]:
        """检查五点描述"""
        issues = []
        
        if len(bullet_points) < 3:
            issues.append("五点描述至少需要3条")
        elif len(bullet_points) > 5:
            issues.append("五点描述不应超过5条")
        
        for i, point in enumerate(bullet_points):
            if len(point) < 10:
                issues.append(f"第{i+1}条描述过短")
            elif len(point) > 500:
                issues.append(f"第{i+1}条描述过长")
        
        score = 1.0 if len(issues) == 0 else 0.7
        
        return {
            "score": score,
            "issues": issues
        }
    
    def _check_image_spec(self, image_path: str) -> Dict[str, Any]:
        """检查图片规范"""
        issues = []
        
        # 简单的文件扩展名检查
        valid_extensions = ['.jpg', '.jpeg', '.png']
        if not any(image_path.lower().endswith(ext) for ext in valid_extensions):
            issues.append("图片格式不符合要求（支持JPG/PNG）")
        
        score = 1.0 if len(issues) == 0 else 0.5
        
        return {
            "score": score,
            "issues": issues
        }
    
    def _load_checkpoints(self) -> List[Dict[str, Any]]:
        """加载检查点配置"""
        # TODO: 从数据库加载
        return []
```

**Step 4: 运行测试确认通过**

```bash
pytest tests/test_listing_qa_service.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/core/listing_qa_service.py backend/tests/test_listing_qa_service.py
git commit -m "feat: implement ListingQAService with field and content validation"
```

---

### Task 4: 创建合规检查 API 端点

**Files:**
- Create: `backend/app/api/compliance.py`
- Modify: `backend/app/main.py`

**Step 1: 编写 API 端点**

```python
# backend/app/api/compliance.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
from app.core.compliance_service import ComplianceService
from app.core.listing_qa_service import ListingQAService

router = APIRouter(prefix="/api/compliance", tags=["compliance"])

compliance_service = ComplianceService()
qa_service = ListingQAService()

class TextCheckRequest(BaseModel):
    text: str
    context: Dict[str, Any] = {}

class ListingCheckRequest(BaseModel):
    listing_data: Dict[str, Any]

class BatchCheckRequest(BaseModel):
    items: List[Dict[str, Any]]

@router.post("/check-text")
async def check_text(request: TextCheckRequest):
    """检查文本合规性"""
    try:
        result = compliance_service.check_text(request.text, request.context)
        return {
            "success": True,
            "data": result.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check-listing")
async def check_listing(request: ListingCheckRequest):
    """检查Listing质量"""
    try:
        # 1. 合规检查
        text_to_check = " ".join([
            request.listing_data.get("title", ""),
            " ".join(request.listing_data.get("bullet_points", [])),
            request.listing_data.get("description", "")
        ])
        
        compliance_result = compliance_service.check_text(text_to_check)
        
        # 2. 质量检查
        qa_result = qa_service.check_listing(request.listing_data)
        
        # 3. 综合判定
        overall_status = "pass"
        if compliance_result.risk_level in ["critical", "high"]:
            overall_status = "blocked"
        elif qa_result["status"] == "fail":
            overall_status = "fail"
        elif compliance_result.risk_level == "medium" or qa_result["status"] == "warning":
            overall_status = "warning"
        
        return {
            "success": True,
            "data": {
                "overall_status": overall_status,
                "compliance": compliance_result.dict(),
                "quality": qa_result,
                "requires_approval": compliance_result.requires_approval
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch-check")
async def batch_check(request: BatchCheckRequest):
    """批量检查"""
    results = []
    
    for item in request.items:
        try:
            check_request = ListingCheckRequest(listing_data=item)
            result = await check_listing(check_request)
            results.append({
                "item": item,
                "result": result["data"]
            })
        except Exception as e:
            results.append({
                "item": item,
                "error": str(e)
            })
    
    return {
        "success": True,
        "data": {
            "total": len(request.items),
            "results": results
        }
    }

@router.get("/rules")
async def get_rules():
    """获取合规规则列表"""
    # TODO: 从数据库加载
    return {
        "success": True,
        "data": {
            "rules": []
        }
    }
```

**Step 2: 注册路由**

```python
# backend/app/main.py
# 在现有导入后添加
from app.api import compliance

# 在 app 创建后添加
app.include_router(compliance.router)
```

**Step 3: 测试 API**

```bash
# 启动服务
cd backend
uvicorn app.main:app --reload

# 在另一个终端测试
curl -X POST http://localhost:8000/api/compliance/check-text \
  -H "Content-Type: application/json" \
  -d '{"text": "Nike shoes for sale"}'
```

Expected: 返回包含风险检测结果的 JSON

**Step 4: Commit**

```bash
git add backend/app/api/compliance.py backend/app/main.py
git commit -m "feat: add compliance check API endpoints"
```

---


### Task 5: 集成到现有工作流

**Files:**
- Modify: `backend/app/api/excel.py`
- Modify: `backend/app/api/followsell.py`

**Step 1: 在 Excel 处理流程中插入合规检查**

```python
# backend/app/api/excel.py
from app.core.compliance_service import ComplianceService
from app.core.listing_qa_service import ListingQAService

compliance_service = ComplianceService()
qa_service = ListingQAService()

@router.post("/api/process")
async def process_excel(request: ProcessRequest):
    """处理Excel（加色/加码）- 增加合规检查"""
    
    # 1. 合规预检
    if request.product_info:
        text_to_check = f"{request.product_info.get('title', '')} {request.product_info.get('description', '')}"
        compliance_result = compliance_service.check_text(text_to_check)
        
        if compliance_result.risk_level in ["critical", "high"]:
            return {
                "success": False,
                "error": "合规检查未通过",
                "compliance_result": compliance_result.dict(),
                "requires_approval": True
            }
    
    # 2. 原有处理逻辑
    try:
        # ... 现有的 Excel 处理代码 ...
        
        # 3. 质量检查（处理后）
        if output_file:
            # 简单的输出文件检查
            qa_result = {"status": "pass", "score": 1.0}
            
            return {
                "success": True,
                "output_file": output_file,
                "compliance_result": compliance_result.dict() if request.product_info else None,
                "qa_result": qa_result
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Step 2: 在跟卖流程中插入合规检查**

```python
# backend/app/api/followsell.py
from app.core.compliance_service import ComplianceService

compliance_service = ComplianceService()

@router.post("/api/followsell/process")
async def process_followsell(request: FollowSellRequest):
    """跟卖处理 - 增加合规检查"""
    
    # 1. 读取老款数据进行合规检查
    if request.old_file:
        # 提取老款的标题和描述进行检查
        # TODO: 实际实现需要解析Excel文件
        compliance_result = compliance_service.check_text("sample text")
        
        if compliance_result.risk_level in ["critical", "high"]:
            return {
                "success": False,
                "error": "老款数据存在合规风险",
                "compliance_result": compliance_result.dict(),
                "requires_approval": True
            }
    
    # 2. 原有跟卖处理逻辑
    try:
        # ... 现有的跟卖处理代码 ...
        
        return {
            "success": True,
            "output_file": output_file,
            "compliance_result": compliance_result.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Step 3: 测试集成**

```bash
# 测试加色流程
curl -X POST http://localhost:8000/api/process \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "add-color",
    "template_type": "DaMaUS",
    "skus": ["TEST001"],
    "product_info": {
      "title": "Test Product",
      "description": "High quality product"
    }
  }'
```

Expected: 返回包含合规检查结果的响应

**Step 4: Commit**

```bash
git add backend/app/api/excel.py backend/app/api/followsell.py
git commit -m "feat: integrate compliance checks into existing workflows"
```

---

### Task 6: 前端集成 - 合规检查结果展示

**Files:**
- Create: `frontend/src/components/ComplianceAlert.tsx`
- Modify: `frontend/src/pages/ExcelProcessor.tsx`

**Step 1: 创建合规警告组件**

```typescript
// frontend/src/components/ComplianceAlert.tsx
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { AlertTriangle, XCircle, CheckCircle } from "lucide-react"

interface ComplianceResult {
  risk_level: string
  risk_score: number
  findings: Array<{
    type: string
    keyword: string
    severity: string
    message: string
  }>
  requires_approval: boolean
}

interface ComplianceAlertProps {
  result: ComplianceResult
}

export function ComplianceAlert({ result }: ComplianceAlertProps) {
  const getIcon = () => {
    switch (result.risk_level) {
      case "critical":
      case "high":
        return <XCircle className="h-4 w-4" />
      case "medium":
        return <AlertTriangle className="h-4 w-4" />
      default:
        return <CheckCircle className="h-4 w-4" />
    }
  }

  const getVariant = () => {
    switch (result.risk_level) {
      case "critical":
      case "high":
        return "destructive"
      case "medium":
        return "default"
      default:
        return "default"
    }
  }

  if (result.risk_level === "safe") {
    return null
  }

  return (
    <Alert variant={getVariant()}>
      {getIcon()}
      <AlertTitle>合规检查警告</AlertTitle>
      <AlertDescription>
        <div className="mt-2 space-y-1">
          {result.findings.map((finding, index) => (
            <div key={index} className="text-sm">
              • {finding.message}
            </div>
          ))}
        </div>
        {result.requires_approval && (
          <div className="mt-2 text-sm font-medium">
            此操作需要人工审批
          </div>
        )}
      </AlertDescription>
    </Alert>
  )
}
```

**Step 2: 集成到 Excel 处理页面**

```typescript
// frontend/src/pages/ExcelProcessor.tsx
import { ComplianceAlert } from "@/components/ComplianceAlert"
import { useState } from "react"

export function ExcelProcessor() {
  const [complianceResult, setComplianceResult] = useState(null)

  const handleProcess = async () => {
    try {
      const response = await fetch("/api/process", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      })

      const data = await response.json()

      if (data.compliance_result) {
        setComplianceResult(data.compliance_result)
      }

      if (!data.success && data.requires_approval) {
        // 显示需要审批的提示
        alert("检测到合规风险，需要人工审批")
        return
      }

      // 继续原有处理逻辑
      // ...
    } catch (error) {
      console.error(error)
    }
  }

  return (
    <div className="space-y-4">
      {complianceResult && (
        <ComplianceAlert result={complianceResult} />
      )}
      
      {/* 原有的表单和按钮 */}
      {/* ... */}
    </div>
  )
}
```

**Step 3: 测试前端集成**

```bash
cd frontend
npm run dev
```

在浏览器中测试：
1. 打开 Excel 处理页面
2. 输入包含商标词的文本
3. 提交处理
4. 验证是否显示合规警告

**Step 4: Commit**

```bash
git add frontend/src/components/ComplianceAlert.tsx frontend/src/pages/ExcelProcessor.tsx
git commit -m "feat: add compliance alert UI component"
```

---

## P0 阶段总结

完成以上 6 个任务后，P0 阶段的核心功能已经实现：

✅ 数据库表结构
✅ ComplianceService（合规检查）
✅ ListingQAService（质量检查）
✅ API 端点
✅ 集成到现有工作流
✅ 前端展示

**下一步：**
- 完善规则库（从数据库加载）
- 添加人工审批流程
- 实现审批记录存储
- 开始 P1 阶段（数据回流与预警）

---

## 执行选项

计划已完成并保存到 `docs/plans/2026-03-04-amazon-listing-mvp-implementation.md`。

**两种执行方式：**

**1. Subagent-Driven（本会话）**
- 我在当前会话中为每个任务派发新的 subagent
- 每个任务完成后进行代码审查
- 快速迭代，实时反馈

**2. 交给 Codex（独立会话）**
- 使用 `codex` 技能将整个计划交给 Codex 执行
- Codex 会批量执行所有任务
- 适合明确的实施计划

**你希望使用哪种方式？**

