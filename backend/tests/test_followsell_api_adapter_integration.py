from __future__ import annotations

from fastapi.testclient import TestClient

from app.api import followsell
from app.main import app


client = TestClient(app)


class FakeAdapter:
    def __init__(self) -> None:
        self.called = False

    def process_followsell(self, req):  # noqa: ANN001
        self.called = True
        return type(
            "Result",
            (),
            {
                "success": True,
                "output_file": "from_followsell_adapter.xlsx",
                "error": None,
                "engine_source": "fake",
            },
        )()


def test_followsell_api_uses_adapter_output(monkeypatch) -> None:
    fake = FakeAdapter()
    monkeypatch.setattr(followsell, "adapter", fake)

    resp = client.post(
        "/api/followsell/process",
        json={
            "old_file": "clean old listing.xlsx",
            "new_file": "new listing.xlsx",
            "old_listing_text": "generic listing without brand",
        },
    )

    assert resp.status_code == 200
    payload = resp.json()
    assert payload["success"] is True
    assert payload["output_file"] == "from_followsell_adapter.xlsx"
    assert payload["engine_source"] == "fake"
    assert fake.called is True


def test_followsell_high_risk_still_blocked_before_adapter_call(monkeypatch) -> None:
    fake = FakeAdapter()
    monkeypatch.setattr(followsell, "adapter", fake)

    resp = client.post(
        "/api/followsell/process",
        json={
            "old_file": "Nike old listing.xlsx",
            "new_file": "new listing.xlsx",
        },
    )

    assert resp.status_code == 200
    payload = resp.json()
    assert payload["success"] is False
    assert payload["requires_approval"] is True
    assert fake.called is False
