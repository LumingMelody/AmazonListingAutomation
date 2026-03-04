from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel

from app.core.competitor_monitor_service import CompetitorMonitorService
from app.core.experiment_service import ExperimentService
from app.models.experiment import ListingLifecycle

router = APIRouter(prefix="/api/experiments", tags=["experiments"])

experiment_service = ExperimentService()
competitor_monitor_service = CompetitorMonitorService()
_lifecycle_store: Dict[str, ListingLifecycle] = {}


class EvaluateListingRequest(BaseModel):
    metrics: Dict[str, Any]


class RecommendationRequest(BaseModel):
    asin: str
    price_analysis: Dict[str, Any]
    rank_analysis: Dict[str, Any]


class LifecycleUpdateRequest(BaseModel):
    status: Optional[str] = None
    stage: Optional[str] = None
    score: Optional[float] = None
    sessions_total: Optional[int] = None
    orders_total: Optional[int] = None
    cvr: Optional[float] = None
    refund_rate: Optional[float] = None
    decision: Optional[str] = None
    decision_reason: Optional[str] = None


@router.post("/evaluate-listing")
async def evaluate_listing(request: EvaluateListingRequest) -> Dict[str, Any]:
    """评估 Listing 指标并给出自动分层决策。"""
    try:
        return experiment_service.evaluate_listing(request.metrics)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/lifecycle")
async def create_or_update_lifecycle(payload: ListingLifecycle) -> Dict[str, Any]:
    """创建或更新 Listing 生命周期记录。"""
    try:
        now = datetime.utcnow()
        existing = _lifecycle_store.get(payload.asin)
        if existing:
            data = existing.model_dump()
            data.update(payload.model_dump(exclude_unset=True))
            data["updated_at"] = now
            record = ListingLifecycle(**data)
        else:
            record_data = payload.model_dump()
            record_data["created_at"] = record_data.get("created_at") or now
            record_data["updated_at"] = now
            record = ListingLifecycle(**record_data)

        _lifecycle_store[record.asin] = record
        return {"success": True, "data": record.model_dump()}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/lifecycle")
async def list_lifecycle(
    asin: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    stage: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """查询 Listing 生命周期记录。"""
    try:
        items = list(_lifecycle_store.values())
        if asin is not None:
            items = [item for item in items if item.asin == asin]
        if status is not None:
            items = [item for item in items if item.status == status]
        if stage is not None:
            items = [item for item in items if item.stage == stage]

        return {"success": True, "items": [item.model_dump() for item in items]}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.patch("/lifecycle/{asin}")
async def update_lifecycle(
    request: LifecycleUpdateRequest,
    asin: str = Path(..., min_length=1),
) -> Dict[str, Any]:
    """更新 Listing 生命周期状态。"""
    try:
        existing = _lifecycle_store.get(asin)
        if existing is None:
            raise HTTPException(status_code=404, detail=f"Lifecycle not found for asin={asin}")

        update_data = request.model_dump(exclude_unset=True)
        if not update_data:
            return {"success": True, "data": existing.model_dump()}

        data = existing.model_dump()
        data.update(update_data)
        data["updated_at"] = datetime.utcnow()
        updated = ListingLifecycle(**data)
        _lifecycle_store[asin] = updated

        return {"success": True, "data": updated.model_dump()}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/recommendations")
async def generate_recommendations(request: RecommendationRequest) -> Dict[str, Any]:
    """生成竞品策略建议。"""
    try:
        recommendations = competitor_monitor_service.generate_recommendations(
            asin=request.asin,
            price_analysis=request.price_analysis,
            rank_analysis=request.rank_analysis,
        )
        return {"success": True, "recommendations": recommendations}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
