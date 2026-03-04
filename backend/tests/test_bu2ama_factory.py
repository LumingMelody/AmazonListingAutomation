from __future__ import annotations

from app.services.bu2ama.adapters import BU2AmaAdapter, LocalFallbackAdapter
from app.services.bu2ama.factory import build_engine_adapter


def test_factory_fallback_when_bu2ama_path_missing(monkeypatch) -> None:
    monkeypatch.setenv("BU2AMA_ENGINE", "auto")
    monkeypatch.setenv("BU2AMA_CORE_PATH", "/not-exists")

    adapter = build_engine_adapter()

    assert isinstance(adapter, LocalFallbackAdapter)


def test_factory_loads_external_adapter_when_path_valid(tmp_path, monkeypatch) -> None:
    core_dir = tmp_path / "core"
    core_dir.mkdir()

    monkeypatch.setenv("BU2AMA_ENGINE", "external")
    monkeypatch.setenv("BU2AMA_CORE_PATH", str(core_dir))
    monkeypatch.setenv("BU2AMA_API_BASE_URL", "http://bu2ama.local")

    adapter = build_engine_adapter()

    assert isinstance(adapter, BU2AmaAdapter)
