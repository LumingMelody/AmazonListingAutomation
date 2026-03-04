from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

SUPPORTED_TRANSFORM_TYPES = {"direct", "lookup", "function", "conditional"}


class MappingRule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule_name: str
    input_fields: list[str] = Field(default_factory=list)
    output_field: str
    transform_type: str
    transform_config: dict[str, Any] = Field(default_factory=dict)
    condition: str | None = None

    @field_validator("transform_type")
    @classmethod
    def validate_transform_type(cls, value: str) -> str:
        if value not in SUPPORTED_TRANSFORM_TYPES:
            allowed_types = ", ".join(sorted(SUPPORTED_TRANSFORM_TYPES))
            raise ValueError(f"Unsupported transform type: {value}. Allowed: {allowed_types}")
        return value
