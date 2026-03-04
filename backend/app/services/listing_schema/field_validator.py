from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, Field

from app.services.listing_schema.field_schema import FieldSchema


class ValidationResult(BaseModel):
    field_name: str
    is_valid: bool
    value: Any | None = None
    errors: list[str] = Field(default_factory=list)
    details: dict[str, "ValidationResult"] | None = None


class FieldValidator:
    def validate_field(self, field_name: str, value: Any, schema: FieldSchema) -> ValidationResult:
        errors: list[str] = []
        normalized_value = value

        if self._is_empty(normalized_value):
            if schema.default_value is not None:
                normalized_value = schema.default_value
            elif schema.required:
                errors.append(f"{field_name} is required")

        if errors:
            return ValidationResult(
                field_name=field_name,
                is_valid=False,
                value=normalized_value,
                errors=errors,
            )

        if self._is_empty(normalized_value):
            return ValidationResult(
                field_name=field_name,
                is_valid=True,
                value=normalized_value,
                errors=[],
            )

        if not self._matches_type(normalized_value, schema.type):
            errors.append(
                f"{field_name} expected type {schema.type}, got {type(normalized_value).__name__}"
            )
            return ValidationResult(
                field_name=field_name,
                is_valid=False,
                value=normalized_value,
                errors=errors,
            )

        if schema.allowed_values is not None:
            if str(normalized_value) not in schema.allowed_values:
                errors.append(
                    f"{field_name} must be one of {schema.allowed_values}, got {normalized_value}"
                )

        if schema.validation_rules:
            errors.extend(self._apply_validation_rules(field_name, normalized_value, schema.validation_rules))

        return ValidationResult(
            field_name=field_name,
            is_valid=not errors,
            value=normalized_value,
            errors=errors,
        )

    def validate_all(
        self,
        data: dict[str, Any],
        schema: dict[str, FieldSchema] | list[FieldSchema] | FieldSchema,
    ) -> dict[str, ValidationResult]:
        schema_map = self._normalize_schema(schema)
        results: dict[str, ValidationResult] = {}

        for field_name, field_schema in schema_map.items():
            field_value = data.get(field_name)
            results[field_name] = self.validate_field(field_name, field_value, field_schema)

        for field_name, field_schema in schema_map.items():
            result = results[field_name]
            if not result.is_valid or not field_schema.dependencies or self._is_empty(result.value):
                continue

            for dependency in field_schema.dependencies:
                dependency_result = results.get(dependency)
                dependency_value = (
                    dependency_result.value if dependency_result is not None else data.get(dependency)
                )
                if self._is_empty(dependency_value):
                    result.is_valid = False
                    result.errors.append(
                        f"{field_name} depends on {dependency}, which is missing or empty"
                    )

        return results

    @staticmethod
    def _normalize_schema(
        schema: dict[str, FieldSchema] | list[FieldSchema] | FieldSchema,
    ) -> dict[str, FieldSchema]:
        if isinstance(schema, FieldSchema):
            return {schema.name: schema}

        if isinstance(schema, list):
            return {item.name: item for item in schema}

        return schema

    @staticmethod
    def _is_empty(value: Any) -> bool:
        return value is None or (isinstance(value, str) and value.strip() == "")

    @staticmethod
    def _matches_type(value: Any, expected_type: str) -> bool:
        if expected_type == "string":
            return isinstance(value, str)
        if expected_type == "int":
            return isinstance(value, int) and not isinstance(value, bool)
        if expected_type == "float":
            return (isinstance(value, float) or isinstance(value, int)) and not isinstance(value, bool)
        if expected_type == "bool":
            return isinstance(value, bool)
        if expected_type == "list":
            return isinstance(value, list)
        if expected_type == "dict":
            return isinstance(value, dict)
        return False

    def _apply_validation_rules(
        self,
        field_name: str,
        value: Any,
        rules: dict[str, Any],
    ) -> list[str]:
        errors: list[str] = []

        min_value = rules.get("min")
        max_value = rules.get("max")
        min_length = rules.get("min_length")
        max_length = rules.get("max_length")
        pattern = rules.get("pattern")
        custom_validator = rules.get("validator")

        if min_value is not None and isinstance(value, (int, float)) and value < min_value:
            errors.append(f"{field_name} must be >= {min_value}")

        if max_value is not None and isinstance(value, (int, float)) and value > max_value:
            errors.append(f"{field_name} must be <= {max_value}")

        if min_length is not None and hasattr(value, "__len__") and len(value) < min_length:
            errors.append(f"{field_name} length must be >= {min_length}")

        if max_length is not None and hasattr(value, "__len__") and len(value) > max_length:
            errors.append(f"{field_name} length must be <= {max_length}")

        if pattern is not None and isinstance(value, str) and not re.match(pattern, value):
            errors.append(f"{field_name} must match pattern {pattern}")

        if callable(custom_validator):
            custom_result = custom_validator(value)
            if isinstance(custom_result, tuple):
                is_valid, message = custom_result
                if not is_valid:
                    errors.append(message or f"{field_name} failed custom validation")
            elif custom_result is False:
                errors.append(f"{field_name} failed custom validation")

        return errors
