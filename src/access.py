"""Load, validate, and query access.yaml."""

from pathlib import Path
import yaml
import jsonschema
from src.schema import ACCESS_YAML_SCHEMA


def load_access(yaml_path: Path) -> dict:
    """Load access.yaml, validate against schema, return parsed dict."""
    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    try:
        jsonschema.validate(data, ACCESS_YAML_SCHEMA)
    except jsonschema.ValidationError as e:
        raise ValueError(f"access.yaml validation error: {e.message} at {list(e.path)}") from e

    # Validate that every tool referenced in access exists in tools
    tool_ids = set(data["tools"].keys())
    for person, grants in data["access"].items():
        for grant in grants:
            if grant["tool"] not in tool_ids:
                raise ValueError(
                    f"access.yaml: '{person}' references unknown tool '{grant['tool']}'. "
                    f"Known tools: {sorted(tool_ids)}"
                )
            # Validate that role exists for this tool
            valid_roles = {r["id"] for r in data["tools"][grant["tool"]]["roles"]}
            if grant["role"] not in valid_roles:
                raise ValueError(
                    f"access.yaml: '{person}' has unknown role '{grant['role']}' "
                    f"for tool '{grant['tool']}'. Valid roles: {sorted(valid_roles)}"
                )

    return data


def role_index(tool_def: dict, role_id: str) -> int:
    """Return the 0-based index of a role in its tool's hierarchy (higher = more privileged)."""
    for i, role in enumerate(tool_def["roles"]):
        if role["id"] == role_id:
            return i
    return -1


def merge_access_into_tree(tree: dict, access_data: dict) -> dict:
    """
    Walk the tree and attach each person's access grants.
    Mutates the tree in place and returns it.
    """
    access_lookup = access_data.get("access", {})

    def _walk(node):
        node["access"] = access_lookup.get(node["name"], [])
        for child in node.get("children", []):
            _walk(child)

    _walk(tree)
    return tree


def query_who_has_role(
    access_data: dict,
    tool_id: str,
    role_id: str | None = None,
    min_role: bool = False,
) -> list[dict]:
    """
    Return list of {name, tool, role, scope, source} for everyone with access
    to the given tool. If role_id is given, filter to that role (or, with
    min_role=True, anyone at that privilege level or higher).
    """
    results = []
    tool_def = access_data["tools"].get(tool_id)
    if tool_def is None:
        return results

    min_idx = role_index(tool_def, role_id) if role_id else -1

    for person, grants in access_data["access"].items():
        for grant in grants:
            if grant["tool"] != tool_id:
                continue
            if role_id:
                person_idx = role_index(tool_def, grant["role"])
                if min_role and person_idx < min_idx:
                    continue
                if not min_role and grant["role"] != role_id:
                    continue
            results.append({"name": person, **grant})

    return results


def query_person_access(access_data: dict, name: str) -> list[dict]:
    """Return all access grants for a given person."""
    return [{"name": name, **g} for g in access_data["access"].get(name, [])]
