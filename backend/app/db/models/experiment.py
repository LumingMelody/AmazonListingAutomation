from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import JSON, Boolean, Date, DateTime, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ExperimentConfigORM(Base):
    __tablename__ = "experiment_configs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    min_sample_size: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    cvr_threshold: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    refund_rate_threshold: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class ListingLifecycleORM(Base):
    __tablename__ = "listing_lifecycle"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    asin: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    sku: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    stage: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    sessions_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    orders_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cvr: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    refund_rate: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    test_start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    test_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    decision: Mapped[str | None] = mapped_column(String(20), nullable=True)
    decision_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class CompetitorSnapshotORM(Base):
    __tablename__ = "competitor_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    asin: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    competitor_asin: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    rating: Mapped[Decimal | None] = mapped_column(Numeric(3, 2), nullable=True)
    review_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    availability: Mapped[str | None] = mapped_column(String(50), nullable=True)
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class ActionRecommendationORM(Base):
    __tablename__ = "action_recommendations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    asin: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    sku: Mapped[str | None] = mapped_column(String(50), nullable=True)
    recommendation_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    priority: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    executed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

