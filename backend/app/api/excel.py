from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.compliance_service import ComplianceService
from app.services.bu2ama.exceptions import EngineExecutionError, EngineNotAvailableError
from app.services.bu2ama.factory import build_engine_adapter
from app.services.bu2ama.types import ProcessRequestDTO

router = APIRouter(tags=["excel"])

compliance_service = ComplianceService()
adapter = build_engine_adapter()


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
        result = adapter.process_excel(
            ProcessRequestDTO(
                mode=request.mode,
                template_type=request.template_type,
                skus=request.skus,
                product_info=request.product_info,
            )
        )

        return {
            "success": result.success,
            "output_file": result.output_file,
            "error": result.error,
            "engine_source": result.engine_source,
            "compliance_result": compliance_result.model_dump() if compliance_result else None,
            "qa_result": {"status": "pass", "score": 1.0} if result.success else {"status": "fail", "score": 0.0},
        }
    except EngineNotAvailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except EngineExecutionError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
