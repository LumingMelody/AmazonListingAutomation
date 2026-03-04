from pathlib import Path


def _read(path: Path) -> str:
    assert path.exists(), f"missing file: {path}"
    return path.read_text(encoding="utf-8")


def test_compliance_alert_component_contract() -> None:
    content = _read(
        Path(__file__).resolve().parents[2] / "frontend" / "src" / "components" / "ComplianceAlert.tsx"
    )
    assert "export interface ComplianceResult" in content
    assert "if (result.risk_level === 'safe')" in content
    assert "此操作需要人工审批" in content


def test_excel_processor_integrates_compliance_alert() -> None:
    content = _read(
        Path(__file__).resolve().parents[2] / "frontend" / "src" / "pages" / "ExcelProcessor.tsx"
    )
    assert "ComplianceAlert" in content
    assert "setComplianceResult" in content
    assert "fetch('/api/process'" in content


def test_app_renders_excel_processor_page() -> None:
    content = _read(Path(__file__).resolve().parents[2] / "frontend" / "src" / "App.tsx")
    assert "ExcelProcessor" in content
    assert "P0: 风险预检与上架质检" in content
