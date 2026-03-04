from __future__ import annotations

import pytest

from app.services.bu2ama.adapters import BU2AmaAdapter, LocalFallbackAdapter
from app.services.bu2ama.exceptions import EngineExecutionError, EngineNotAvailableError
from app.services.bu2ama.types import FollowSellRequestDTO, ProcessRequestDTO


def test_local_adapter_returns_standardized_result() -> None:
    adapter = LocalFallbackAdapter()

    result = adapter.process_excel(
        ProcessRequestDTO(mode="add-color", template_type="DaMaUS", skus=["SKU1"])
    )

    assert result.success is True
    assert result.output_file is not None
    assert result.output_file.endswith(".xlsx")
    assert result.engine_source in {"local", "bu2ama"}


def test_external_adapter_normalizes_output_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeResponse:
        status_code = 200

        @staticmethod
        def json() -> dict[str, object]:
            return {
                "success": True,
                "output_file": "from_bu2ama.xlsx",
                "error": None,
            }

    def fake_post(*args, **kwargs):  # noqa: ANN002, ANN003
        return FakeResponse()

    monkeypatch.setattr("app.services.bu2ama.adapters.requests.post", fake_post)

    adapter = BU2AmaAdapter(api_base_url="http://bu2ama.local", timeout_seconds=0.1)
    result = adapter.process_excel(
        ProcessRequestDTO(mode="add-color", template_type="DaMaUS", skus=["SKU1"])
    )

    assert result.success is True
    assert result.output_file == "from_bu2ama.xlsx"
    assert result.error is None
    assert result.engine_source == "bu2ama"


def test_external_adapter_raises_engine_execution_error_on_crash(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeResponse:
        status_code = 500

        @staticmethod
        def json() -> dict[str, object]:
            return {"detail": "engine crashed"}

    def fake_post(*args, **kwargs):  # noqa: ANN002, ANN003
        return FakeResponse()

    monkeypatch.setattr("app.services.bu2ama.adapters.requests.post", fake_post)

    adapter = BU2AmaAdapter(api_base_url="http://bu2ama.local", timeout_seconds=0.1)

    with pytest.raises(EngineExecutionError):
        adapter.process_followsell(FollowSellRequestDTO(old_file="old.xlsx", new_file="new.xlsx"))


def test_external_adapter_raises_not_available_when_connection_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_post(*args, **kwargs):  # noqa: ANN002, ANN003
        raise ConnectionError("connection refused")

    monkeypatch.setattr("app.services.bu2ama.adapters.requests.post", fake_post)

    adapter = BU2AmaAdapter(api_base_url="http://127.0.0.1:9", timeout_seconds=0.1)

    with pytest.raises(EngineNotAvailableError):
        adapter.process_excel(
            ProcessRequestDTO(mode="add-color", template_type="DaMaUS", skus=["SKU1"])
        )
