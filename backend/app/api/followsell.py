from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.compliance_service import ComplianceService

router = APIRouter(tags=["followsell"])

compliance_service = ComplianceService()


class FollowSellRequest(BaseModel):
    old_file: str
    new_file: str
    old_listing_text: Optional[str] = None


@router.post("/api/followsell/process")
async def process_followsell(request: FollowSellRequest) -> Dict[str, Any]:
    try:
        text_to_check = request.old_listing_text or request.old_file
        compliance_result = compliance_service.check_text(text_to_check)

        if compliance_result.risk_level in {"critical", "high"}:
            return {
                "success": False,
                "error": "老款数据存在合规风险",
                "compliance_result": compliance_result.model_dump(),
                "requires_approval": True,
            }

        output_file = f"followsell_{request.new_file}"
        return {
            "success": True,
            "output_file": output_file,
            "compliance_result": compliance_result.model_dump(),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
