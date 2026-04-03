"""JSON Schema for access.yaml validation."""

ACCESS_YAML_SCHEMA = {
    "type": "object",
    "required": ["version", "tools", "access"],
    "properties": {
        "version": {"type": "string"},
        "tools": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "required": ["display_name", "color", "roles"],
                "properties": {
                    "display_name": {"type": "string"},
                    "color": {"type": "string", "pattern": "^#[0-9A-Fa-f]{6}$"},
                    "badge_threshold": {"type": "integer", "minimum": 0},
                    "roles": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["id", "label"],
                            "properties": {
                                "id": {"type": "string"},
                                "label": {"type": "string"},
                            },
                        },
                    },
                },
            },
        },
        "access": {
            "type": "object",
            "additionalProperties": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["tool", "role", "source"],
                    "properties": {
                        "tool": {"type": "string"},
                        "role": {"type": "string"},
                        "scope": {"type": ["string", "null"]},
                        "source": {"type": "string"},
                        "fetched_at": {"type": "string"},
                    },
                },
            },
        },
    },
}
