from __future__ import annotations

from typing import Protocol

from app.services.bu2ama.types import FollowSellRequestDTO, ProcessRequestDTO, ProcessResultDTO


class EngineAdapter(Protocol):
    def process_excel(self, req: ProcessRequestDTO) -> ProcessResultDTO: ...

    def process_followsell(self, req: FollowSellRequestDTO) -> ProcessResultDTO: ...
