from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.core.data_import_service import DataImportService

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

data_import_service = DataImportService()


class ImportRequest(BaseModel):
    data: List[Dict[str, Any]]


@router.post("/import/ad-performance")
async def import_ad_performance(request: ImportRequest) -> Dict[str, Any]:
    """导入广告表现数据"""
    try:
        result = data_import_service.import_ad_performance(request.data)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/import/listing-metrics")
async def import_listing_metrics(request: ImportRequest) -> Dict[str, Any]:
    """导入 Listing 指标数据"""
    try:
        result = data_import_service.import_listing_metrics(request.data)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/metrics/summary")
async def get_metrics_summary(days: int = Query(7, ge=1, le=90)) -> Dict[str, Any]:
    """获取指标汇总"""
    try:
        # TODO: implement actual aggregation from imported data.
        return {
            "success": True,
            "data": {
                "period": f"last_{days}_days",
                "total_sessions": 0,
                "total_orders": 0,
                "total_sales": 0.0,
                "avg_cvr": 0.0,
            },
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
