from pathlib import Path

import re

import pytest

from app.models.compliance import (
    Action,
    BlacklistKeyword,
    ComplianceCheckResult,
    ComplianceRule,
    QACheckpoint,
    RuleType,
    Severity,
)


def test_migration_file_exists_and_has_required_tables() -> None:
    migration = Path(__file__).resolve().parents[1] / "migrations" / "001_compliance_tables.sql"
    assert migration.exists(), "migration SQL file should exist"

    sql = migration.read_text(encoding="utf-8").lower()
    for table in [
        "compliance_rules",
        "blacklist_keywords",
        "qa_checkpoints",
        "approval_records",
        "compliance_check_results",
    ]:
        assert re.search(rf"create table( if not exists)? {table}\b", sql)


def test_compliance_rule_model_uses_enums() -> None:
    rule = ComplianceRule(
        rule_type=RuleType.TRADEMARK,
        pattern="nike",
        severity=Severity.CRITICAL,
        action=Action.BLOCK,
    )
    assert rule.rule_type == RuleType.TRADEMARK
    assert rule.severity == Severity.CRITICAL
    assert rule.action == Action.BLOCK


@pytest.mark.parametrize(
    "payload",
    [
        {"keyword": "Nike", "language": "en"},
        {
            "job_id": "job-1",
            "check_type": "text",
            "status": "fail",
            "findings": {"items": []},
        },
        {
            "checkpoint_name": "title-length",
            "checkpoint_type": "field_completeness",
            "validation_rule": {"min": 20},
        },
    ],
)
def test_other_models_construct(payload: dict) -> None:
    if "keyword" in payload:
        model = BlacklistKeyword(**payload)
        assert model.language == "en"
    elif "job_id" in payload:
        model = ComplianceCheckResult(**payload)
        assert model.status == "fail"
    else:
        model = QACheckpoint(**payload)
        assert model.weight == 1.0
