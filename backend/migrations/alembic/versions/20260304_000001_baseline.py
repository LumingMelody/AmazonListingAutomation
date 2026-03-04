"""baseline schema

Revision ID: 20260304_000001
Revises:
Create Date: 2026-03-04 14:30:00
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260304_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "compliance_rules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("rule_type", sa.String(length=50), nullable=False),
        sa.Column("pattern", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("action", sa.String(length=20), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "blacklist_keywords",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("keyword", sa.String(length=200), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=True),
        sa.Column("language", sa.String(length=10), nullable=False, server_default="en"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_blacklist_keyword", "blacklist_keywords", ["keyword"])

    op.create_table(
        "qa_checkpoints",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("checkpoint_name", sa.String(length=100), nullable=False),
        sa.Column("checkpoint_type", sa.String(length=50), nullable=False),
        sa.Column("validation_rule", sa.JSON(), nullable=False),
        sa.Column("weight", sa.Numeric(3, 2), nullable=False, server_default="1.0"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "approval_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_id", sa.String(length=50), nullable=False),
        sa.Column("job_type", sa.String(length=50), nullable=False),
        sa.Column("risk_level", sa.String(length=20), nullable=True),
        sa.Column("approver", sa.String(length=100), nullable=True),
        sa.Column("action", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_approval_job_id", "approval_records", ["job_id"])

    op.create_table(
        "compliance_check_results",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_id", sa.String(length=50), nullable=False),
        sa.Column("check_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("findings", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_compliance_result_job_id", "compliance_check_results", ["job_id"])

    op.create_table(
        "ad_performance",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("campaign_id", sa.String(length=100), nullable=False),
        sa.Column("ad_group_id", sa.String(length=100), nullable=True),
        sa.Column("keyword", sa.String(length=200), nullable=True),
        sa.Column("impressions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("clicks", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("spend", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("sales", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("orders", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_ad_performance_campaign_date", "ad_performance", ["campaign_id", "date"])
    op.create_index("idx_ad_performance_date", "ad_performance", ["date"])

    op.create_table(
        "listing_metrics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("asin", sa.String(length=20), nullable=False),
        sa.Column("sku", sa.String(length=50), nullable=True),
        sa.Column("sessions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("page_views", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("units_ordered", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("units_ordered_b2b", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("unit_session_percentage", sa.Numeric(5, 2), nullable=True),
        sa.Column("ordered_product_sales", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("total_order_items", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_listing_metrics_asin_date", "listing_metrics", ["asin", "date"])
    op.create_index("idx_listing_metrics_sku_date", "listing_metrics", ["sku", "date"])

    op.create_table(
        "alert_rules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("rule_name", sa.String(length=100), nullable=False),
        sa.Column("metric_name", sa.String(length=50), nullable=False),
        sa.Column("condition", sa.String(length=20), nullable=False),
        sa.Column("threshold_value", sa.Numeric(10, 4), nullable=False),
        sa.Column("time_window", sa.Integer(), nullable=False, server_default="24"),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "alert_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("rule_id", sa.Integer(), sa.ForeignKey("alert_rules.id"), nullable=True),
        sa.Column("asin", sa.String(length=20), nullable=True),
        sa.Column("sku", sa.String(length=50), nullable=True),
        sa.Column("metric_value", sa.Numeric(10, 4), nullable=True),
        sa.Column("threshold_value", sa.Numeric(10, 4), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("severity", sa.String(length=20), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
    )
    op.create_index("idx_alert_history_status", "alert_history", ["status"])
    op.create_index("idx_alert_history_created_at", "alert_history", ["created_at"])

    op.create_table(
        "experiment_configs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=True),
        sa.Column("min_sample_size", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("cvr_threshold", sa.Numeric(5, 4), nullable=True),
        sa.Column("refund_rate_threshold", sa.Numeric(5, 4), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "listing_lifecycle",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("asin", sa.String(length=20), nullable=False),
        sa.Column("sku", sa.String(length=50), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("stage", sa.String(length=20), nullable=False),
        sa.Column("score", sa.Numeric(5, 2), nullable=True),
        sa.Column("sessions_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("orders_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("cvr", sa.Numeric(5, 4), nullable=True),
        sa.Column("refund_rate", sa.Numeric(5, 4), nullable=True),
        sa.Column("test_start_date", sa.Date(), nullable=True),
        sa.Column("test_end_date", sa.Date(), nullable=True),
        sa.Column("decision", sa.String(length=20), nullable=True),
        sa.Column("decision_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_lifecycle_asin", "listing_lifecycle", ["asin"])
    op.create_index("idx_lifecycle_status", "listing_lifecycle", ["status"])
    op.create_index("idx_lifecycle_stage", "listing_lifecycle", ["stage"])

    op.create_table(
        "competitor_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("asin", sa.String(length=20), nullable=False),
        sa.Column("competitor_asin", sa.String(length=20), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=True),
        sa.Column("rating", sa.Numeric(3, 2), nullable=True),
        sa.Column("review_count", sa.Integer(), nullable=True),
        sa.Column("rank", sa.Integer(), nullable=True),
        sa.Column("availability", sa.String(length=50), nullable=True),
        sa.Column("snapshot_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_competitor_asin_date", "competitor_snapshots", ["asin", "snapshot_date"])
    op.create_index("idx_competitor_competitor_asin", "competitor_snapshots", ["competitor_asin"])

    op.create_table(
        "action_recommendations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("asin", sa.String(length=20), nullable=False),
        sa.Column("sku", sa.String(length=50), nullable=True),
        sa.Column("recommendation_type", sa.String(length=50), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("data", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("executed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("idx_action_recommendation_asin_status", "action_recommendations", ["asin", "status"])
    op.create_index("idx_action_recommendation_type", "action_recommendations", ["recommendation_type"])


def downgrade() -> None:
    op.drop_index("idx_action_recommendation_type", table_name="action_recommendations")
    op.drop_index("idx_action_recommendation_asin_status", table_name="action_recommendations")
    op.drop_table("action_recommendations")

    op.drop_index("idx_competitor_competitor_asin", table_name="competitor_snapshots")
    op.drop_index("idx_competitor_asin_date", table_name="competitor_snapshots")
    op.drop_table("competitor_snapshots")

    op.drop_index("idx_lifecycle_stage", table_name="listing_lifecycle")
    op.drop_index("idx_lifecycle_status", table_name="listing_lifecycle")
    op.drop_index("idx_lifecycle_asin", table_name="listing_lifecycle")
    op.drop_table("listing_lifecycle")

    op.drop_table("experiment_configs")

    op.drop_index("idx_alert_history_created_at", table_name="alert_history")
    op.drop_index("idx_alert_history_status", table_name="alert_history")
    op.drop_table("alert_history")

    op.drop_table("alert_rules")

    op.drop_index("idx_listing_metrics_sku_date", table_name="listing_metrics")
    op.drop_index("idx_listing_metrics_asin_date", table_name="listing_metrics")
    op.drop_table("listing_metrics")

    op.drop_index("idx_ad_performance_date", table_name="ad_performance")
    op.drop_index("idx_ad_performance_campaign_date", table_name="ad_performance")
    op.drop_table("ad_performance")

    op.drop_index("idx_compliance_result_job_id", table_name="compliance_check_results")
    op.drop_table("compliance_check_results")

    op.drop_index("idx_approval_job_id", table_name="approval_records")
    op.drop_table("approval_records")

    op.drop_table("qa_checkpoints")

    op.drop_index("idx_blacklist_keyword", table_name="blacklist_keywords")
    op.drop_table("blacklist_keywords")

    op.drop_table("compliance_rules")

