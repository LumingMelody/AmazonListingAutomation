from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

SUPPORTED_FIELD_TYPES = {"string", "int", "float", "bool", "list", "dict"}


class FieldSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    type: str
    required: bool = False
    position: int = Field(ge=1)
    allowed_values: list[str] | None = None
    default_value: Any | None = None
    dependencies: list[str] | None = None
    validation_rules: dict[str, Any] | None = None

    @field_validator("type")
    @classmethod
    def validate_type(cls, value: str) -> str:
        if value not in SUPPORTED_FIELD_TYPES:
            allowed_types = ", ".join(sorted(SUPPORTED_FIELD_TYPES))
            raise ValueError(f"Unsupported field type: {value}. Allowed: {allowed_types}")
        return value
