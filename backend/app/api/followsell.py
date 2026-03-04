from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.compliance_service import ComplianceService
from app.services.bu2ama.exceptions import EngineExecutionError, EngineNotAvailableError
from app.services.bu2ama.factory import build_engine_adapter
from app.services.bu2ama.types import FollowSellRequestDTO

router = APIRouter(tags=["followsell"])

compliance_service = ComplianceService()
adapter = build_engine_adapter()


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

        result = adapter.process_followsell(
            FollowSellRequestDTO(
                old_file=request.old_file,
                new_file=request.new_file,
                old_listing_text=request.old_listing_text,
            )
        )
        return {
            "success": result.success,
            "output_file": result.output_file,
            "error": result.error,
            "engine_source": result.engine_source,
            "compliance_result": compliance_result.model_dump(),
        }
    except EngineNotAvailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except EngineExecutionError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
