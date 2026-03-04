from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from pydantic import BaseModel


class ExperimentConfig(BaseModel):
    id: Optional[int] = None
    name: str
    category: Optional[str] = None
    min_sample_size: int = 100
    cvr_threshold: Optional[Decimal] = None
    refund_rate_threshold: Optional[Decimal] = None
    active: bool = True
    created_at: Optional[datetime] = None


class ListingLifecycle(BaseModel):
    id: Optional[int] = None
    asin: str
    sku: Optional[str] = None
    status: str
    stage: str
    score: Optional[Decimal] = None
    sessions_total: int = 0
    orders_total: int = 0
    cvr: Optional[Decimal] = None
    refund_rate: Optional[Decimal] = None
    test_start_date: Optional[date] = None
    test_end_date: Optional[date] = None
    decision: Optional[str] = None
    decision_reason: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CompetitorSnapshot(BaseModel):
    id: Optional[int] = None
    asin: str
    competitor_asin: str
    price: Optional[Decimal] = None
    rating: Optional[Decimal] = None
    review_count: Optional[int] = None
    rank: Optional[int] = None
    availability: Optional[str] = None
    snapshot_date: date
    created_at: Optional[datetime] = None


class ActionRecommendation(BaseModel):
    id: Optional[int] = None
    asin: str
    sku: Optional[str] = None
    recommendation_type: str
    priority: str
    title: str
    description: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    status: str = "pending"
    created_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None
