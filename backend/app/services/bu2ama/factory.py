from __future__ import annotations

import os
from pathlib import Path

import requests

from app.config import BU2AMA_API_BASE_URL, BU2AMA_CORE_PATH, BU2AMA_ENGINE
from app.services.bu2ama.adapters import BU2AmaAdapter, LocalFallbackAdapter
from app.services.bu2ama.interfaces import EngineAdapter


def _core_path_exists(core_path: str) -> bool:
    if not core_path:
        return False
    return Path(core_path).expanduser().exists()


def _external_api_available(api_base_url: str, timeout_seconds: float) -> bool:
    try:
        response = requests.get(f"{api_base_url.rstrip('/')}/health", timeout=min(timeout_seconds, 1.0))
        return 200 <= response.status_code < 300
    except Exception:
        return False


def build_engine_adapter(
    engine_mode: str | None = None,
    *,
    core_path: str | None = None,
    api_base_url: str | None = None,
    timeout_seconds: float | None = None,
) -> EngineAdapter:
    mode = (engine_mode or os.getenv("BU2AMA_ENGINE") or BU2AMA_ENGINE or "auto").strip().lower()
    resolved_core_path = core_path or os.getenv("BU2AMA_CORE_PATH") or BU2AMA_CORE_PATH
    resolved_api_base_url = api_base_url or os.getenv("BU2AMA_API_BASE_URL") or BU2AMA_API_BASE_URL
    resolved_timeout = timeout_seconds
    if resolved_timeout is None:
        resolved_timeout = float(os.getenv("BU2AMA_TIMEOUT_SECONDS", "30"))

    if mode == "local":
        return LocalFallbackAdapter()

    if mode == "external":
        if _core_path_exists(resolved_core_path):
            return BU2AmaAdapter(api_base_url=resolved_api_base_url, timeout_seconds=resolved_timeout)
        return LocalFallbackAdapter()

    if mode == "auto":
        if _core_path_exists(resolved_core_path) and _external_api_available(resolved_api_base_url, resolved_timeout):
            return BU2AmaAdapter(api_base_url=resolved_api_base_url, timeout_seconds=resolved_timeout)
        return LocalFallbackAdapter()

    return LocalFallbackAdapter()
