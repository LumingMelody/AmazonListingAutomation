from __future__ import annotations

from pathlib import Path
from typing import Any

import requests

from app.services.bu2ama.exceptions import EngineExecutionError, EngineNotAvailableError
from app.services.bu2ama.interfaces import EngineAdapter
from app.services.bu2ama.types import FollowSellRequestDTO, ProcessRequestDTO, ProcessResultDTO


class BU2AmaAdapter(EngineAdapter):
    def __init__(self, api_base_url: str, timeout_seconds: float = 30.0) -> None:
        if not api_base_url:
            raise ValueError("api_base_url is required")
        self.api_base_url = api_base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.api_base_url}{path}"
        try:
            response = requests.post(url, json=payload, timeout=self.timeout_seconds)
        except Exception as exc:  # requests exceptions + test monkeypatch exceptions
            raise EngineNotAvailableError(str(exc)) from exc

        try:
            data = response.json()
        except ValueError:
            data = {}

        if response.status_code >= 500:
            raise EngineExecutionError(data.get("detail") or data.get("error") or "Engine execution failed")
        if response.status_code >= 400:
            raise EngineExecutionError(data.get("detail") or data.get("error") or "Engine request failed")

        return data

    @staticmethod
    def _normalize_result(data: dict[str, Any]) -> ProcessResultDTO:
        success = bool(data.get("success", False))
        nested_data = data.get("data") if isinstance(data.get("data"), dict) else {}

        output_file = data.get("output_file") or data.get("output_filename")
        if not output_file and nested_data:
            output_file = nested_data.get("output_file") or nested_data.get("output_filename")

        error = data.get("error") or data.get("detail")
        if not error and nested_data:
            error = nested_data.get("error")

        return ProcessResultDTO(
            success=success,
            output_file=str(output_file) if output_file is not None else None,
            error=str(error) if error is not None else None,
            engine_source="bu2ama",
        )

    def process_excel(self, req: ProcessRequestDTO) -> ProcessResultDTO:
        payload = {
            "mode": req.mode,
            "template_type": req.template_type,
            "skus": req.skus,
            "product_info": req.product_info,
        }
        data = self._post_json("/api/process", payload)
        return self._normalize_result(data)

    def process_followsell(self, req: FollowSellRequestDTO) -> ProcessResultDTO:
        payload = {
            "old_file": req.old_file,
            "new_file": req.new_file,
            "old_listing_text": req.old_listing_text,
        }
        data = self._post_json("/api/followsell/process", payload)
        return self._normalize_result(data)


class LocalFallbackAdapter(EngineAdapter):
    def process_excel(self, req: ProcessRequestDTO) -> ProcessResultDTO:
        return ProcessResultDTO(
            success=True,
            output_file=f"processed_{req.mode}_{req.template_type}.xlsx",
            error=None,
            engine_source="local",
        )

    def process_followsell(self, req: FollowSellRequestDTO) -> ProcessResultDTO:
        filename = Path(req.new_file).name
        return ProcessResultDTO(
            success=True,
            output_file=f"followsell_{filename}",
            error=None,
            engine_source="local",
        )
