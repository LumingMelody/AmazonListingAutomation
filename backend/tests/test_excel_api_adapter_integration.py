from __future__ import annotations

from fastapi.testclient import TestClient

from app.api import excel
from app.main import app


client = TestClient(app)


class FakeAdapter:
    def __init__(self) -> None:
        self.called = False

    def process_excel(self, req):  # noqa: ANN001
        self.called = True
        return type(
            "Result",
            (),
            {
                "success": True,
                "output_file": "from_adapter.xlsx",
                "error": None,
                "engine_source": "fake",
            },
        )()


def test_excel_api_uses_adapter_output(monkeypatch) -> None:
    fake = FakeAdapter()
    monkeypatch.setattr(excel, "adapter", fake)

    resp = client.post(
        "/api/process",
        json={
            "mode": "add-color",
            "template_type": "DaMaUS",
            "skus": ["SKU1"],
            "product_info": {
                "title": "clean title",
                "description": "clean description",
            },
        },
    )

    assert resp.status_code == 200
    payload = resp.json()
    assert payload["success"] is True
    assert payload["output_file"] == "from_adapter.xlsx"
    assert payload["engine_source"] == "fake"
    assert fake.called is True


def test_high_risk_listing_still_blocked_before_adapter_call(monkeypatch) -> None:
    fake = FakeAdapter()
    monkeypatch.setattr(excel, "adapter", fake)

    resp = client.post(
        "/api/process",
        json={
            "mode": "add-color",
            "template_type": "DaMaUS",
            "skus": ["SKU1"],
            "product_info": {
                "title": "Nike special product",
                "description": "clean description",
            },
        },
    )

    assert resp.status_code == 200
    payload = resp.json()
    assert payload["success"] is False
    assert payload["requires_approval"] is True
    assert fake.called is False
