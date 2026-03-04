import pytest

from app.core.compliance_service import ComplianceService


@pytest.fixture
def compliance_service() -> ComplianceService:
    return ComplianceService()


def test_check_trademark_violation(compliance_service: ComplianceService) -> None:
    result = compliance_service.check_text("Nike shoes for sale")

    assert result.risk_level in ["high", "critical"]
    assert any("trademark" == f["type"] for f in result.findings)
    assert result.requires_approval is True


def test_check_clean_text(compliance_service: ComplianceService) -> None:
    result = compliance_service.check_text("High quality running shoes")

    assert result.risk_level == "safe"
    assert len(result.findings) == 0
    assert result.requires_approval is False


def test_check_forbidden_words(compliance_service: ComplianceService) -> None:
    result = compliance_service.check_text("Best product ever, guaranteed cure")

    assert result.risk_level in ["medium", "high", "critical"]
    assert any("forbidden_word" == f["type"] for f in result.findings)
