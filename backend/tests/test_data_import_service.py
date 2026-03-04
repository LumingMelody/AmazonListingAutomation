import pytest

from app.core.data_import_service import DataImportService


@pytest.fixture
def import_service() -> DataImportService:
    return DataImportService()


def test_import_ad_performance_data(import_service: DataImportService) -> None:
    data = [
        {
            "campaign_id": "CAMP001",
            "impressions": 1000,
            "clicks": 50,
            "spend": "25.50",
            "date": "2026-03-01",
        }
    ]

    result = import_service.import_ad_performance(data)
    assert result["success"] is True
    assert result["imported"] == 1


def test_import_listing_metrics(import_service: DataImportService) -> None:
    data = [
        {
            "asin": "B001",
            "sku": "SKU001",
            "sessions": 500,
            "units_ordered": 10,
            "date": "2026-03-01",
        }
    ]

    result = import_service.import_listing_metrics(data)
    assert result["success"] is True
    assert result["imported"] == 1
