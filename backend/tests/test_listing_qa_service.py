import pytest

from app.core.listing_qa_service import ListingQAService


@pytest.fixture
def qa_service() -> ListingQAService:
    return ListingQAService()


def test_check_field_completeness(qa_service: ListingQAService) -> None:
    listing_data = {
        "title": "High Quality Running Shoes for Men",
        "bullet_points": [
            "Breathable and lightweight design for all-day comfort",
            "Durable sole suitable for road and gym training",
            "Non-slip outsole improves traction on wet surfaces",
        ],
        "description": "A durable pair of running shoes designed for daily exercise.",
        "main_image": "image.jpg",
        "price": 29.99,
    }

    result = qa_service.check_listing(listing_data)
    assert result["score"] > 0.8
    assert result["status"] == "pass"


def test_incomplete_listing(qa_service: ListingQAService) -> None:
    listing_data = {
        "title": "Test Product",
    }

    result = qa_service.check_listing(listing_data)
    assert result["score"] < 0.5
    assert result["status"] == "fail"
    assert len(result["issues"]) > 0


def test_title_validation(qa_service: ListingQAService) -> None:
    short_result = qa_service.validate_title("Short")
    assert short_result["valid"] is False

    valid_result = qa_service.validate_title("High Quality Running Shoes for Men")
    assert valid_result["valid"] is True
