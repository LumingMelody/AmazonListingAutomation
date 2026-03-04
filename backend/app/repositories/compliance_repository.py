from app.db.models.compliance import ComplianceRuleORM
from app.repositories.base import BaseRepository


class ComplianceRuleRepository(BaseRepository):
    def create(
        self,
        *,
        rule_type: str,
        pattern: str,
        severity: str,
        action: str,
        active: bool = True,
    ) -> ComplianceRuleORM:
        model = ComplianceRuleORM(
            rule_type=rule_type,
            pattern=pattern,
            severity=severity,
            action=action,
            active=active,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

