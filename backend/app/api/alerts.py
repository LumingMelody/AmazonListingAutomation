from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel

from app.core.alert_service import AlertService

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

alert_service = AlertService()


class CheckMetricsRequest(BaseModel):
    metrics: Dict[str, Any]


class ResolveAlertRequest(BaseModel):
    reason: str


@router.post("/check")
async def check_metrics(request: CheckMetricsRequest) -> Dict[str, Any]:
    """检查指标并生成预警。"""
    try:
        alerts = alert_service.check_metrics(request.metrics)
        return {"alerts": alerts}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/active")
async def get_active_alerts() -> Dict[str, Any]:
    """获取活跃预警列表。"""
    try:
        # TODO: 从数据库查询活跃预警
        return {"success": True, "alerts": []}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int = Path(..., ge=1),
    request: ResolveAlertRequest | None = None,
) -> Dict[str, Any]:
    """解决预警。"""
    try:
        _ = request
        # TODO: 更新数据库中的预警状态
        return {"success": True, "message": f"Alert {alert_id} resolved"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
