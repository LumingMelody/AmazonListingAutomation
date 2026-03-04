from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.services.listing_schema import (
    FieldSchema,
    FieldValidator,
    MappingRule,
    MappingService,
    RuleEngine,
)


def test_field_schema_accepts_valid_configuration() -> None:
    schema = FieldSchema(
        name="title",
        type="string",
        required=True,
        position=1,
        allowed_values=None,
        default_value=None,
        dependencies=None,
        validation_rules={"min_length": 3, "max_length": 100},
    )

    assert schema.name == "title"
    assert schema.type == "string"
    assert schema.required is True


def test_field_schema_rejects_unsupported_type() -> None:
    with pytest.raises(ValidationError):
        FieldSchema(name="price", type="decimal", required=True, position=2)


def test_mapping_rule_rejects_unsupported_transform_type() -> None:
    with pytest.raises(ValidationError):
        MappingRule(
            rule_name="invalid_rule",
            input_fields=["sku"],
            output_field="asin",
            transform_type="script",
            transform_config={},
        )


def test_field_validator_marks_required_field_missing() -> None:
    validator = FieldValidator()
    schema = FieldSchema(name="title", type="string", required=True, position=1)

    result = validator.validate_field("title", None, schema)

    assert result.is_valid is False
    assert "required" in result.errors[0]


def test_field_validator_uses_default_value() -> None:
    validator = FieldValidator()
    schema = FieldSchema(
        name="currency",
        type="string",
        required=False,
        position=3,
        default_value="USD",
    )

    result = validator.validate_field("currency", None, schema)

    assert result.is_valid is True
    assert result.value == "USD"


def test_field_validator_checks_allowed_values_and_pattern() -> None:
    validator = FieldValidator()
    schema = FieldSchema(
        name="country",
        type="string",
        required=True,
        position=4,
        allowed_values=["US", "CA"],
        validation_rules={"pattern": r"^[A-Z]{2}$"},
    )

    invalid_choice = validator.validate_field("country", "UK", schema)
    invalid_pattern = validator.validate_field("country", "u1", schema)

    assert invalid_choice.is_valid is False
    assert "must be one of" in invalid_choice.errors[0]
    assert invalid_pattern.is_valid is False
    assert any("must match pattern" in error for error in invalid_pattern.errors)


def test_field_validator_applies_custom_validator() -> None:
    validator = FieldValidator()
    schema = FieldSchema(
        name="quantity",
        type="int",
        required=True,
        position=5,
        validation_rules={"validator": lambda v: (v % 2 == 0, "quantity must be even")},
    )

    result = validator.validate_field("quantity", 3, schema)

    assert result.is_valid is False
    assert result.errors == ["quantity must be even"]


def test_validate_all_checks_dependencies() -> None:
    validator = FieldValidator()
    schema_set = {
        "country": FieldSchema(name="country", type="string", required=False, position=1),
        "state": FieldSchema(
            name="state",
            type="string",
            required=False,
            position=2,
            dependencies=["country"],
        ),
    }

    results = validator.validate_all({"state": "CA"}, schema_set)

    assert results["state"].is_valid is False
    assert "depends on country" in results["state"].errors[0]


def test_rule_engine_direct_transform_single_field() -> None:
    engine = RuleEngine()
    rule = MappingRule(
        rule_name="copy_title",
        input_fields=["title"],
        output_field="listing_title",
        transform_type="direct",
        transform_config={},
    )

    value = engine.apply_rule(rule, {"title": "Coffee Mug"})

    assert value == "Coffee Mug"


def test_rule_engine_lookup_transform_case_insensitive() -> None:
    engine = RuleEngine()
    rule = MappingRule(
        rule_name="normalize_color",
        input_fields=["color"],
        output_field="color_code",
        transform_type="lookup",
        transform_config={
            "lookup_map": {"red": "R", "blue": "B"},
            "default": "UNK",
            "case_sensitive": False,
        },
    )

    value = engine.apply_rule(rule, {"color": "RED"})

    assert value == "R"


def test_rule_engine_function_transform_sum() -> None:
    engine = RuleEngine()
    rule = MappingRule(
        rule_name="total_cost",
        input_fields=["item_price", "shipping"],
        output_field="total",
        transform_type="function",
        transform_config={"function_name": "sum"},
    )

    value = engine.apply_rule(rule, {"item_price": 19.5, "shipping": 5.5})

    assert value == pytest.approx(25.0)


def test_rule_engine_function_transform_callable() -> None:
    engine = RuleEngine()
    rule = MappingRule(
        rule_name="callable_transform",
        input_fields=["first", "second"],
        output_field="combined",
        transform_type="function",
        transform_config={"callable": lambda first, second: f"{first}-{second}"},
    )

    value = engine.apply_rule(rule, {"first": "A", "second": "B"})

    assert value == "A-B"


def test_rule_engine_conditional_transform_uses_true_branch() -> None:
    engine = RuleEngine()
    rule = MappingRule(
        rule_name="high_value_flag",
        input_fields=["price"],
        output_field="flag",
        transform_type="conditional",
        transform_config={
            "expression": "price >= 100",
            "true_value": "HIGH",
            "false_value": "NORMAL",
        },
    )

    value = engine.apply_rule(rule, {"price": 150})

    assert value == "HIGH"


def test_rule_engine_apply_all_rules_skips_unmatched_condition() -> None:
    engine = RuleEngine()
    rules = [
        MappingRule(
            rule_name="title",
            input_fields=["title"],
            output_field="title_out",
            transform_type="direct",
            transform_config={},
        ),
        MappingRule(
            rule_name="premium_tag",
            input_fields=[],
            output_field="tag",
            transform_type="direct",
            transform_config={"default": "PREMIUM"},
            condition="price > 100",
        ),
    ]

    mapped = engine.apply_all_rules(rules, {"title": "Desk Lamp", "price": 49})

    assert mapped == {"title_out": "Desk Lamp"}


def test_mapping_service_load_schema_and_rules() -> None:
    status_schema = FieldSchema(
        name="status",
        type="string",
        required=True,
        position=1,
        allowed_values=["OK", "FAIL"],
    )
    rules = [
        MappingRule(
            rule_name="copy_status",
            input_fields=["raw_status"],
            output_field="status",
            transform_type="direct",
            transform_config={},
        )
    ]
    service = MappingService(schemas={"status_schema": status_schema}, rules={"demo": rules})

    loaded_schema = service.load_schema("status_schema")
    loaded_rules = service.load_rules("demo")

    assert loaded_schema.name == "status"
    assert len(loaded_rules) == 1


def test_mapping_service_maps_and_validates_single_field_schema() -> None:
    status_schema = FieldSchema(
        name="status",
        type="string",
        required=True,
        position=1,
        allowed_values=["OK", "FAIL"],
    )
    rules = [
        MappingRule(
            rule_name="copy_status",
            input_fields=["raw_status"],
            output_field="status",
            transform_type="direct",
            transform_config={},
        )
    ]
    service = MappingService(schemas={"status_schema": status_schema}, rules={"demo": rules})

    mapped = service.map_fields("demo", {"raw_status": "OK"})
    result = service.validate_fields(mapped, "status_schema")

    assert mapped == {"status": "OK"}
    assert result.is_valid is True


def test_mapping_service_validates_schema_set_with_aggregated_result() -> None:
    listing_schema = [
        FieldSchema(name="title", type="string", required=True, position=1),
        FieldSchema(name="price", type="float", required=True, position=2, validation_rules={"min": 0}),
    ]
    service = MappingService(schemas={"listing": listing_schema})

    result = service.validate_fields({"title": "", "price": -1}, "listing")

    assert result.is_valid is False
    assert result.details is not None
    assert result.details["title"].is_valid is False
    assert result.details["price"].is_valid is False


def test_mapping_service_load_schema_raises_for_multi_field_schema_set() -> None:
    service = MappingService(
        schemas={
            "listing": [
                FieldSchema(name="title", type="string", required=True, position=1),
                FieldSchema(name="price", type="float", required=True, position=2),
            ]
        }
    )

    with pytest.raises(KeyError):
        service.load_schema("listing")


def test_mapping_service_raises_for_missing_schema_or_rule() -> None:
    service = MappingService()

    with pytest.raises(KeyError):
        service.load_schema("missing")

    with pytest.raises(KeyError):
        service.load_rules("missing")
