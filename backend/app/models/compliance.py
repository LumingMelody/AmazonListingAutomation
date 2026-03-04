from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


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
    risk_level: str
    risk_score: float
    findings: List[Dict[str, Any]]
    requires_approval: bool
    blocked_reasons: List[str] = []
