from __future__ import annotations

from typing import Any

from app.services.listing_schema.mapping_rule import MappingRule


class RuleEngine:
    def apply_rule(self, rule: MappingRule, input_data: dict[str, Any]) -> Any:
        if rule.condition and not self._matches_condition(rule.condition, input_data):
            return None

        if rule.transform_type == "direct":
            return self._direct_transform(rule, input_data)

        if rule.transform_type == "lookup":
            return self._lookup_transform(rule, input_data)

        if rule.transform_type == "function":
            return self._function_transform(rule, input_data)

        if rule.transform_type == "conditional":
            return self._conditional_transform(rule, input_data)

        raise ValueError(f"Unsupported transform type: {rule.transform_type}")

    def apply_all_rules(
        self,
        rules: list[MappingRule],
        input_data: dict[str, Any],
    ) -> dict[str, Any]:
        mapped_data: dict[str, Any] = {}

        for rule in rules:
            if rule.condition and not self._matches_condition(rule.condition, input_data):
                continue
            mapped_data[rule.output_field] = self.apply_rule(rule, input_data)

        return mapped_data

    @staticmethod
    def _matches_condition(condition: str, input_data: dict[str, Any]) -> bool:
        if not condition:
            return True

        try:
            return bool(eval(condition, {"__builtins__": {}}, dict(input_data)))  # noqa: S307
        except Exception:
            return False

    @staticmethod
    def _direct_transform(rule: MappingRule, input_data: dict[str, Any]) -> Any:
        if not rule.input_fields:
            return rule.transform_config.get("default")

        if len(rule.input_fields) == 1:
            field_name = rule.input_fields[0]
            return input_data.get(field_name, rule.transform_config.get("default"))

        join_with = rule.transform_config.get("join_with")
        if join_with is not None:
            return str(join_with).join(
                "" if input_data.get(field_name) is None else str(input_data.get(field_name))
                for field_name in rule.input_fields
            )

        return {field_name: input_data.get(field_name) for field_name in rule.input_fields}

    @staticmethod
    def _lookup_transform(rule: MappingRule, input_data: dict[str, Any]) -> Any:
        source_field = rule.transform_config.get("source_field")
        if source_field is None:
            if not rule.input_fields:
                return rule.transform_config.get("default")
            source_field = rule.input_fields[0]

        source_value = input_data.get(source_field)
        lookup_map = rule.transform_config.get("lookup_map", {})
        default_value = rule.transform_config.get("default")
        case_sensitive = bool(rule.transform_config.get("case_sensitive", True))

        if not isinstance(lookup_map, dict):
            raise ValueError("lookup_map must be a dictionary")

        if source_value in lookup_map:
            return lookup_map[source_value]

        if not case_sensitive and isinstance(source_value, str):
            for key, mapped_value in lookup_map.items():
                if isinstance(key, str) and key.lower() == source_value.lower():
                    return mapped_value

        return default_value

    def _function_transform(self, rule: MappingRule, input_data: dict[str, Any]) -> Any:
        values = [input_data.get(field_name) for field_name in rule.input_fields]
        transform_config = rule.transform_config

        callable_fn = transform_config.get("callable")
        if callable(callable_fn):
            return callable_fn(*values)

        function_name = str(transform_config.get("function_name", "")).strip().lower()
        if function_name == "upper":
            return "" if not values else str(values[0]).upper()

        if function_name == "lower":
            return "" if not values else str(values[0]).lower()

        if function_name == "concat":
            separator = str(transform_config.get("separator", ""))
            return separator.join("" if value is None else str(value) for value in values)

        if function_name == "join":
            separator = str(transform_config.get("separator", ","))
            return separator.join("" if value is None else str(value) for value in values)

        if function_name == "sum":
            return sum(float(value or 0) for value in values)

        if function_name == "template":
            template = str(transform_config.get("template", ""))
            return template.format(**input_data)

        raise ValueError(f"Unsupported function transform: {function_name or 'undefined'}")

    def _conditional_transform(self, rule: MappingRule, input_data: dict[str, Any]) -> Any:
        expression = rule.transform_config.get("expression") or rule.condition
        condition_met = self._matches_condition(str(expression), input_data) if expression else False

        if condition_met:
            return self._resolve_conditional_branch("true", rule, input_data)
        return self._resolve_conditional_branch("false", rule, input_data)

    def _resolve_conditional_branch(
        self,
        branch_prefix: str,
        rule: MappingRule,
        input_data: dict[str, Any],
    ) -> Any:
        field_key = f"{branch_prefix}_field"
        value_key = f"{branch_prefix}_value"
        function_key = f"{branch_prefix}_function"

        if field_key in rule.transform_config:
            return input_data.get(str(rule.transform_config[field_key]))

        if value_key in rule.transform_config:
            return rule.transform_config[value_key]

        function_config = rule.transform_config.get(function_key)
        if isinstance(function_config, dict):
            branch_rule = MappingRule(
                rule_name=f"{rule.rule_name}_{branch_prefix}_branch",
                input_fields=list(function_config.get("input_fields", rule.input_fields)),
                output_field=rule.output_field,
                transform_type="function",
                transform_config=function_config,
            )
            return self._function_transform(branch_rule, input_data)

        if callable(function_config):
            return function_config(input_data)

        return None
