from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.models.analytics import ListingMetricsORM
from app.db.models.compliance import ComplianceRuleORM
from app.db.models.experiment import ListingLifecycleORM
from app.db.session import check_database_connection, get_db
from app.main import app
from app.repositories.analytics_repository import ListingMetricsRepository
from app.repositories.compliance_repository import ComplianceRuleRepository
from app.repositories.experiment_repository import ListingLifecycleRepository


def _sqlite_session_factory(tmp_path):
    db_file = tmp_path / "task1.sqlite"
    engine = create_engine(f"sqlite+pysqlite:///{db_file}", future=True)
    Base.metadata.create_all(bind=engine)
    return engine, sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def test_alembic_baseline_exists() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    alembic_ini = repo_root / "alembic.ini"
    env_py = repo_root / "migrations" / "alembic" / "env.py"
    versions_dir = repo_root / "migrations" / "alembic" / "versions"

    assert alembic_ini.exists(), "alembic.ini should be present"
    assert env_py.exists(), "Alembic env.py should be present"
    assert versions_dir.exists() and any(versions_dir.glob("*.py")), "baseline revision should exist"


def test_orm_metadata_contains_required_task1_tables() -> None:
    table_names = set(Base.metadata.tables.keys())

    for required in {
        "compliance_rules",
        "blacklist_keywords",
        "qa_checkpoints",
        "ad_performance",
        "listing_metrics",
        "experiment_configs",
        "listing_lifecycle",
        "competitor_snapshots",
        "action_recommendations",
    }:
        assert required in table_names

    assert ComplianceRuleORM.__tablename__ == "compliance_rules"
    assert ListingMetricsORM.__tablename__ == "listing_metrics"
    assert ListingLifecycleORM.__tablename__ == "listing_lifecycle"


def test_session_helpers_use_real_database_connection(tmp_path) -> None:
    engine, session_factory = _sqlite_session_factory(tmp_path)

    assert check_database_connection(session_factory=session_factory) is True

    db_gen = get_db(session_factory=session_factory)
    db = next(db_gen)
    assert db.is_active is True
    db_gen.close()
    engine.dispose()


def test_repositories_can_persist_and_query_records(tmp_path) -> None:
    engine, session_factory = _sqlite_session_factory(tmp_path)

    with session_factory() as db:
        compliance_repo = ComplianceRuleRepository(db)
        metrics_repo = ListingMetricsRepository(db)
        lifecycle_repo = ListingLifecycleRepository(db)

        created_rule = compliance_repo.create(
            rule_type="trademark",
            pattern="nike",
            severity="critical",
            action="block",
        )
        assert created_rule.id is not None

        metrics_repo.create(
            asin="B00DBTASK1",
            sku="SKU-DB-1",
            sessions=120,
            page_views=160,
            units_ordered=10,
            ordered_product_sales="199.99",
            date="2026-03-04",
        )
        listed_metrics = metrics_repo.list_by_asin("B00DBTASK1")
        assert len(listed_metrics) == 1
        assert listed_metrics[0].asin == "B00DBTASK1"

        lifecycle = lifecycle_repo.upsert_by_asin(
            asin="B00DBTASK1",
            status="testing",
            stage="test",
            sessions_total=120,
            orders_total=10,
        )
        assert lifecycle.id is not None

        lifecycle_updated = lifecycle_repo.upsert_by_asin(
            asin="B00DBTASK1",
            status="active",
            stage="scale",
            decision="add_variants",
        )
        assert lifecycle_updated.id == lifecycle.id
        assert lifecycle_updated.status == "active"

    engine.dispose()


def test_health_endpoint_checks_database_connection(monkeypatch) -> None:
    monkeypatch.setattr("app.main.check_database_connection", lambda: True)

    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
