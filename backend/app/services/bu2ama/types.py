from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ProcessRequestDTO(BaseModel):
    mode: str
    template_type: str
    skus: list[str] = Field(default_factory=list)
    product_info: dict[str, Any] | None = None


class FollowSellRequestDTO(BaseModel):
    old_file: str
    new_file: str
    old_listing_text: str | None = None


class ProcessResultDTO(BaseModel):
    success: bool
    output_file: str | None = None
    error: str | None = None
    engine_source: str
