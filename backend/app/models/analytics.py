from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class AdPerformance(BaseModel):
    id: Optional[int] = None
    campaign_id: str
    ad_group_id: Optional[str] = None
    keyword: Optional[str] = None
    impressions: int = 0
    clicks: int = 0
    spend: Decimal = Decimal("0")
    sales: Decimal = Decimal("0")
    orders: int = 0
    date: date
    created_at: Optional[datetime] = None


class ListingMetrics(BaseModel):
    id: Optional[int] = None
    asin: str
    sku: Optional[str] = None
    sessions: int = 0
    page_views: int = 0
    units_ordered: int = 0
    units_ordered_b2b: int = 0
    unit_session_percentage: Optional[Decimal] = None
    ordered_product_sales: Decimal = Decimal("0")
    total_order_items: int = 0
    date: date
    created_at: Optional[datetime] = None


class AlertRule(BaseModel):
    id: Optional[int] = None
    rule_name: str
    metric_name: str
    condition: str
    threshold_value: Decimal
    time_window: int = 24
    severity: str
    active: bool = True
    created_at: Optional[datetime] = None


class AlertHistory(BaseModel):
    id: Optional[int] = None
    rule_id: int
    asin: Optional[str] = None
    sku: Optional[str] = None
    metric_value: Decimal
    threshold_value: Decimal
    message: str
    severity: str
    status: str = "pending"
    created_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
