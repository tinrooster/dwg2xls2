from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import re
import jsonschema
from pathlib import Path

class ValidationLevel(Enum):
    STRICT = "strict"
    WARN = "warn"
    FLEXIBLE = "flexible"

@dataclass
class ValidationRule:
    """Defines a validation rule"""
    field: str
    rule_type: str
    parameters: Dict[str, Any]
    message: str
    level: ValidationLevel

class ConfigValidator:
    """Validates facility configurations"""

    # Basic validation schemas
    ROOM_SCHEMA = {
        "type": "object",
        "required": ["id", "name", "description"],
        "properties": {
            "id": {
                "type": "string",
                "pattern": "^[A-Z0-9_]+$"
            },
            "name": {"type": "string"},
            "description": {"type": "string"},
            "attributes": {"type": "object"},
            "parent_room": {"type": ["string", "null"]}
        }
    }

    RACK_TYPE_SCHEMA = {
        "type": "object",
        "required": ["id", "name", "description"],
        "properties": {
            "id": {
                "type": "string",
                "pattern": "^[A-Z_]+$"
            },
            "name": {"type": "string"},
            "description": {"type": "string"},
            "default_height": {
                "type": "integer",
                "minimum": 1,
                "maximum": 100
            },
            "attributes": {"type": "object"}
        }
    }

    RACK_SERIES_SCHEMA = {
        "type": "object",
        "required": ["prefix", "start_number", "end_number", "rack_type", "room"],
        "properties": {
            "prefix": {
                "type": "string",
                "pattern": "^[A-Z]{2,3}$"
            },
            "start_number": {
                "type": "integer",
                "minimum": 1
            },
            "end_number": {
                "type": "integer",
                "minimum": 1
            },
            "rack_type": {"type": "string"},
            "room": {"type": "string"},
            "description": {"type": "string"},
            "attributes": {"type": "object"}
        }
    }

    def __init__(self, validation_level: ValidationLevel = ValidationLevel.STRICT):
        self.validation_level = validation_level
        self.custom_rules: List[ValidationRule] = []

    def add_custom_rule(self, rule: ValidationRule):
        """Add a custom validation rule"""
        self.custom_rules.append(rule)

    def validate_room(self, room_data: Dict[str, Any]) -> List[str]:
        """Validate room configuration"""
        errors = []
        
        try:
            jsonschema.validate(instance=room_data, schema=self.ROOM_SCHEMA)
        except jsonschema.exceptions.ValidationError as e:
            errors.append(f"Room validation error: {str(e)}")

        # Custom rules
        for rule in self.custom_rules:
            if rule.field.startswith('room.'):
                if not self._check_custom_rule(room_data, rule):
                    if rule.level == self.validation_level:
                        errors.append(rule.message)

        return errors

    def validate_rack_type(self, rack_type_data: Dict[str, Any]) -> List[str]:
        """Validate rack type configuration"""
        errors = []
        
        try:
            jsonschema.validate(instance=rack_type_data, schema=self.RACK_TYPE_SCHEMA)
        except jsonschema.exceptions.ValidationError as e:
            errors.append(f"Rack type validation error: {str(e)}")

        return errors

    def _check_custom_rule(self, data: Dict[str, Any], rule: ValidationRule) -> bool:
        """Check a custom validation rule"""
        if rule.rule_type == "regex":
            value = data.get(rule.field.split('.')[-1], "")
            return re.match(rule.parameters["pattern"], str(value)) is not None
        elif rule.rule_type == "range":
            value = data.get(rule.field.split('.')[-1], 0)
            return rule.parameters["min"] <= value <= rule.parameters["max"]
        return True
