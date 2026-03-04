from decimal import Decimal
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.competitor_monitor_service import CompetitorMonitorService

router = APIRouter(prefix="/api/competitor-monitor", tags=["competitor-monitor"])

competitor_monitor_service = CompetitorMonitorService()


class TrackCompetitorRequest(BaseModel):
    asin: str
    competitor_asin: str
    current_price: Decimal
    historical_prices: List[Dict[str, Any]] = Field(default_factory=list)
    current_rank: int | None = None
    historical_ranks: List[int] = Field(default_factory=list)


class PriceAnalysisRequest(BaseModel):
    asin: str
    current_price: Decimal
    historical_prices: List[Dict[str, Any]] = Field(default_factory=list)


class RecommendationsRequest(BaseModel):
    asin: str
    price_analysis: Dict[str, Any]
    rank_analysis: Dict[str, Any]


@router.post("/track")
async def track_competitor(request: TrackCompetitorRequest) -> Dict[str, Any]:
    """追踪竞品并返回价格和排名分析。"""
    try:
        price_analysis = competitor_monitor_service.analyze_price_changes(
            asin=request.asin,
            current_price=request.current_price,
            historical_prices=request.historical_prices,
        )

        if request.current_rank is None:
            rank_analysis = {"status": "new", "change": 0}
        else:
            rank_analysis = competitor_monitor_service.detect_rank_changes(
                current_rank=request.current_rank,
                historical_ranks=request.historical_ranks,
            )

        return {
            "success": True,
            "asin": request.asin,
            "competitor_asin": request.competitor_asin,
            "price_analysis": price_analysis,
            "rank_analysis": rank_analysis,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/price-analysis")
async def analyze_price(request: PriceAnalysisRequest) -> Dict[str, Any]:
    """分析竞品价格变化趋势。"""
    try:
        analysis = competitor_monitor_service.analyze_price_changes(
            asin=request.asin,
            current_price=request.current_price,
            historical_prices=request.historical_prices,
        )
        return {"analysis": analysis}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/recommendations")
async def generate_recommendations(request: RecommendationsRequest) -> Dict[str, Any]:
    """基于竞品分析生成动作建议。"""
    try:
        recommendations = competitor_monitor_service.generate_recommendations(
            asin=request.asin,
            price_analysis=request.price_analysis,
            rank_analysis=request.rank_analysis,
        )
        return {"recommendations": recommendations}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
