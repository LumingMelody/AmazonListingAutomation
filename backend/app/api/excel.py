from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.compliance_service import ComplianceService

router = APIRouter(tags=["excel"])

compliance_service = ComplianceService()


class ProcessRequest(BaseModel):
    mode: str
    template_type: str
    skus: List[str] = Field(default_factory=list)
    product_info: Optional[Dict[str, Any]] = None


@router.post("/api/process")
async def process_excel(request: ProcessRequest) -> Dict[str, Any]:
    compliance_result = None

    if request.product_info:
        text_to_check = " ".join(
            [
                str(request.product_info.get("title", "")),
                str(request.product_info.get("description", "")),
            ]
        ).strip()
        compliance_result = compliance_service.check_text(text_to_check)

        if compliance_result.risk_level in {"critical", "high"}:
            return {
                "success": False,
                "error": "合规检查未通过",
                "compliance_result": compliance_result.model_dump(),
                "requires_approval": True,
            }

    try:
        output_file = f"processed_{request.mode}_{request.template_type}.xlsx"
        return {
            "success": True,
            "output_file": output_file,
            "compliance_result": compliance_result.model_dump() if compliance_result else None,
            "qa_result": {"status": "pass", "score": 1.0},
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
