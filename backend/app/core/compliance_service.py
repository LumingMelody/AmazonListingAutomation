import re
from typing import Any, Dict, List, Optional

from app.models.compliance import RiskAssessment


class ComplianceService:
    """Listing 文本合规检查服务。"""

    SEVERITY_SCORE = {
        "critical": 4,
        "high": 3,
        "medium": 2,
        "low": 1,
    }

    def check_text(self, text: str, context: Optional[Dict[str, Any]] = None) -> RiskAssessment:
        _ = context
        findings: List[Dict[str, Any]] = []

        findings.extend(self._check_trademarks(text))
        findings.extend(self._check_ip_words(text))
        findings.extend(self._check_forbidden_words(text))

        max_severity_score = max((self.SEVERITY_SCORE.get(f["severity"], 0) for f in findings), default=0)

        if max_severity_score >= 4:
            risk_level = "critical"
        elif max_severity_score >= 3:
            risk_level = "high"
        elif max_severity_score >= 2:
            risk_level = "medium"
        elif max_severity_score >= 1:
            risk_level = "low"
        else:
            risk_level = "safe"

        risk_score = (
            sum(self.SEVERITY_SCORE.get(f["severity"], 0) for f in findings) / len(findings)
            if findings
            else 0.0
        )

        requires_approval = risk_level in {"critical", "high"}
        blocked_reasons = [f["message"] for f in findings if f["action"] == "block"]

        return RiskAssessment(
            risk_level=risk_level,
            risk_score=risk_score,
            findings=findings,
            requires_approval=requires_approval,
            blocked_reasons=blocked_reasons,
        )

    def _check_trademarks(self, text: str) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []
        trademarks = [
            "Nike",
            "Adidas",
            "Apple",
            "Samsung",
            "Sony",
            "Disney",
            "Marvel",
            "Pokemon",
            "Louis Vuitton",
        ]

        lowered = text.lower()
        for trademark in trademarks:
            if trademark.lower() in lowered:
                findings.append(
                    {
                        "type": "trademark",
                        "keyword": trademark,
                        "severity": "critical",
                        "action": "block",
                        "message": f"检测到商标词: {trademark}",
                    }
                )

        return findings

    def _check_ip_words(self, text: str) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []
        ip_words = [
            "Harry Potter",
            "Star Wars",
            "Batman",
            "Superman",
            "Mickey Mouse",
            "Hello Kitty",
        ]

        lowered = text.lower()
        for word in ip_words:
            if word.lower() in lowered:
                findings.append(
                    {
                        "type": "ip",
                        "keyword": word,
                        "severity": "critical",
                        "action": "block",
                        "message": f"检测到IP词: {word}",
                    }
                )

        return findings

    def _check_forbidden_words(self, text: str) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []
        patterns = [
            (r"\bcure\b", "cure", "high", "医疗宣称"),
            (r"\bguaranteed\b", "guaranteed", "medium", "绝对化承诺"),
            (r"\bbest\s+ever\b", "best ever", "medium", "夸大宣传"),
            (r"\b100%\s+safe\b", "100% safe", "high", "绝对化安全承诺"),
        ]

        lowered = text.lower()
        for pattern, keyword, severity, reason in patterns:
            if re.search(pattern, lowered):
                findings.append(
                    {
                        "type": "forbidden_word",
                        "keyword": keyword,
                        "severity": severity,
                        "action": "warn" if severity == "medium" else "review",
                        "message": f"检测到禁用词: {keyword} ({reason})",
                    }
                )

        return findings
