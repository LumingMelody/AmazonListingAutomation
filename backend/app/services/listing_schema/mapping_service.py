from __future__ import annotations

from typing import Any

from app.services.listing_schema.field_schema import FieldSchema
from app.services.listing_schema.field_validator import FieldValidator, ValidationResult
from app.services.listing_schema.mapping_rule import MappingRule
from app.services.listing_schema.rule_engine import RuleEngine

SchemaDefinition = FieldSchema | list[FieldSchema] | dict[str, FieldSchema]


class MappingService:
    def __init__(
        self,
        *,
        schemas: dict[str, SchemaDefinition] | None = None,
        rules: dict[str, list[MappingRule]] | None = None,
        field_validator: FieldValidator | None = None,
        rule_engine: RuleEngine | None = None,
    ) -> None:
        self.field_validator = field_validator or FieldValidator()
        self.rule_engine = rule_engine or RuleEngine()
        self._single_schemas: dict[str, FieldSchema] = {}
        self._schema_sets: dict[str, dict[str, FieldSchema]] = {}
        self._rules: dict[str, list[MappingRule]] = rules or {}

        if schemas:
            for schema_name, schema_definition in schemas.items():
                self.register_schema(schema_name, schema_definition)

    def register_schema(self, schema_name: str, schema_definition: SchemaDefinition) -> None:
        if isinstance(schema_definition, FieldSchema):
            self._single_schemas[schema_name] = schema_definition
            return

        if isinstance(schema_definition, list):
            if not all(isinstance(item, FieldSchema) for item in schema_definition):
                raise TypeError("All schema list items must be FieldSchema")
            self._schema_sets[schema_name] = {item.name: item for item in schema_definition}
            return

        if isinstance(schema_definition, dict):
            if not all(isinstance(value, FieldSchema) for value in schema_definition.values()):
                raise TypeError("All schema dict values must be FieldSchema")
            self._schema_sets[schema_name] = dict(schema_definition)
            return

        raise TypeError("schema_definition must be FieldSchema, list[FieldSchema], or dict[str, FieldSchema]")

    def register_rules(self, template_type: str, rules: list[MappingRule]) -> None:
        self._rules[template_type] = rules

    def load_schema(self, schema_name: str) -> FieldSchema:
        if schema_name in self._single_schemas:
            return self._single_schemas[schema_name]

        if schema_name in self._schema_sets:
            schema_set = self._schema_sets[schema_name]
            if len(schema_set) == 1:
                return next(iter(schema_set.values()))
            raise KeyError(
                f"Schema '{schema_name}' contains multiple fields. Use validate_fields for schema set validation."
            )

        raise KeyError(f"Schema '{schema_name}' not found")

    def load_rules(self, template_type: str) -> list[MappingRule]:
        if template_type not in self._rules:
            raise KeyError(f"Rules for template_type '{template_type}' not found")
        return self._rules[template_type]

    def map_fields(self, template_type: str, input_data: dict[str, Any]) -> dict[str, Any]:
        rules = self.load_rules(template_type)
        return self.rule_engine.apply_all_rules(rules, input_data)

    def validate_fields(self, mapped_data: dict[str, Any], schema_name: str) -> ValidationResult:
        if schema_name in self._schema_sets:
            field_results = self.field_validator.validate_all(mapped_data, self._schema_sets[schema_name])
            all_valid = all(result.is_valid for result in field_results.values())
            errors = [
                f"{field_name}: {error}"
                for field_name, result in field_results.items()
                for error in result.errors
            ]
            return ValidationResult(
                field_name=schema_name,
                is_valid=all_valid,
                value=mapped_data,
                errors=errors,
                details=field_results,
            )

        schema = self.load_schema(schema_name)
        field_value = mapped_data.get(schema.name)
        return self.field_validator.validate_field(schema.name, field_value, schema)
