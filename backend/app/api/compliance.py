from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.compliance_service import ComplianceService
from app.core.listing_qa_service import ListingQAService

router = APIRouter(prefix="/api/compliance", tags=["compliance"])

compliance_service = ComplianceService()
qa_service = ListingQAService()


class TextCheckRequest(BaseModel):
    text: str
    context: Dict[str, Any] = Field(default_factory=dict)


class ListingCheckRequest(BaseModel):
    listing_data: Dict[str, Any]


class BatchCheckRequest(BaseModel):
    items: List[Dict[str, Any]]


@router.post("/check-text")
async def check_text(request: TextCheckRequest) -> Dict[str, Any]:
    try:
        result = compliance_service.check_text(request.text, request.context)
        return {"success": True, "data": result.model_dump()}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/check-listing")
async def check_listing(request: ListingCheckRequest) -> Dict[str, Any]:
    try:
        listing_data = request.listing_data
        text_to_check = " ".join(
            [
                listing_data.get("title", ""),
                " ".join(listing_data.get("bullet_points", [])),
                listing_data.get("description", ""),
            ]
        ).strip()

        compliance_result = compliance_service.check_text(text_to_check)
        qa_result = qa_service.check_listing(listing_data)

        overall_status = "pass"
        if compliance_result.risk_level in {"critical", "high"}:
            overall_status = "blocked"
        elif qa_result["status"] == "fail":
            overall_status = "fail"
        elif compliance_result.risk_level == "medium" or qa_result["status"] == "warning":
            overall_status = "warning"

        return {
            "success": True,
            "data": {
                "overall_status": overall_status,
                "compliance": compliance_result.model_dump(),
                "quality": qa_result,
                "requires_approval": compliance_result.requires_approval,
            },
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/batch-check")
async def batch_check(request: BatchCheckRequest) -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []

    for item in request.items:
        try:
            listing_request = ListingCheckRequest(listing_data=item)
            result = await check_listing(listing_request)
            results.append({"item": item, "result": result["data"]})
        except Exception as exc:
            results.append({"item": item, "error": str(exc)})

    return {"success": True, "data": {"total": len(request.items), "results": results}}


@router.get("/rules")
async def get_rules() -> Dict[str, Any]:
    return {"success": True, "data": {"rules": []}}
