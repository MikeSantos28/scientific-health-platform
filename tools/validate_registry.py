#!/usr/bin/env python3
"""Dependency-free structural validation for the Phase 1 Tool Registry.

Registry files use JSON-compatible YAML, so JSON parsing is sufficient without
installing a YAML library. This program never installs or runs scientific tools.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


TOOLS_DIR = Path(__file__).resolve().parent
REGISTRY_PATH = TOOLS_DIR / "registry.yaml"
EXPECTED_TOOL_IDS = {"fastp", "megahit", "diamond"}
REQUIRED_TOOL_FIELDS = {
    "id", "name", "version", "description", "domain", "category", "inputs",
    "outputs", "parameters", "resources", "execution", "container",
    "documentation", "limitations",
}
REQUIRED_DATA_ITEM_FIELDS = {"id", "required", "type", "format", "biological_meaning", "description"}
REQUIRED_PARAMETER_FIELDS = {"id", "type", "description", "required"}
REQUIRED_EXECUTION_ENVIRONMENTS = {"local", "container", "colab", "cloud"}
VALID_EXECUTION_STATUSES = {"supported", "planned", "unvalidated"}


class RegistryValidationError(ValueError):
    """Raised when declarative registry metadata violates the Phase 1 contract."""


def load_yaml(path: Path) -> dict[str, Any]:
    """Load a JSON-compatible YAML mapping without external dependencies."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RegistryValidationError(f"Missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RegistryValidationError(f"Invalid JSON-compatible YAML in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise RegistryValidationError(f"Expected mapping in {path}")
    return data


def validate_data_items(tool_id: str, field: str, items: Any) -> None:
    if not isinstance(items, list) or not items:
        raise RegistryValidationError(f"{tool_id}: {field} must be a non-empty list")
    for item in items:
        if not isinstance(item, dict) or REQUIRED_DATA_ITEM_FIELDS - item.keys():
            raise RegistryValidationError(f"{tool_id}: every {field} entry needs {sorted(REQUIRED_DATA_ITEM_FIELDS)}")
        if not isinstance(item["required"], bool) or not isinstance(item["format"], list) or not item["format"]:
            raise RegistryValidationError(f"{tool_id}: invalid required/format metadata in {field}")


def validate_definition(tool_id: str, definition: dict[str, Any]) -> None:
    missing = REQUIRED_TOOL_FIELDS - definition.keys()
    if missing:
        raise RegistryValidationError(f"{tool_id}: missing required fields: {sorted(missing)}")
    if definition["id"] != tool_id:
        raise RegistryValidationError(f"{tool_id}: definition id does not match registry id")
    for text_field in ("name", "version", "description", "domain", "category"):
        if not isinstance(definition[text_field], str) or not definition[text_field].strip():
            raise RegistryValidationError(f"{tool_id}: {text_field} must be a non-empty string")
    validate_data_items(tool_id, "inputs", definition["inputs"])
    validate_data_items(tool_id, "outputs", definition["outputs"])
    if not isinstance(definition["parameters"], list):
        raise RegistryValidationError(f"{tool_id}: parameters must be a list")
    for parameter in definition["parameters"]:
        if not isinstance(parameter, dict) or REQUIRED_PARAMETER_FIELDS - parameter.keys():
            raise RegistryValidationError(f"{tool_id}: every parameter needs {sorted(REQUIRED_PARAMETER_FIELDS)}")
        if not isinstance(parameter["required"], bool):
            raise RegistryValidationError(f"{tool_id}: parameter required must be boolean")
    resources = definition["resources"]
    if not isinstance(resources, dict) or {"cpu", "memory", "disk", "gpu_required"} - resources.keys():
        raise RegistryValidationError(f"{tool_id}: incomplete resources metadata")
    if not isinstance(resources["gpu_required"], bool):
        raise RegistryValidationError(f"{tool_id}: gpu_required must be boolean")
    execution = definition["execution"]
    if not isinstance(execution, dict) or REQUIRED_EXECUTION_ENVIRONMENTS - execution.keys():
        raise RegistryValidationError(f"{tool_id}: incomplete execution metadata")
    for environment in REQUIRED_EXECUTION_ENVIRONMENTS:
        entry = execution[environment]
        if not isinstance(entry, dict) or not isinstance(entry.get("compatible"), bool) or entry.get("status") not in VALID_EXECUTION_STATUSES:
            raise RegistryValidationError(f"{tool_id}: invalid execution entry for {environment}")
    container = definition["container"]
    if not isinstance(container, dict) or {"supported", "image", "registry"} - container.keys():
        raise RegistryValidationError(f"{tool_id}: incomplete container metadata")
    if not isinstance(container["supported"], bool) or any(
        value is not None and not isinstance(value, str) for value in (container["image"], container["registry"])
    ):
        raise RegistryValidationError(f"{tool_id}: invalid container metadata types")
    documentation = definition["documentation"]
    if (
        not isinstance(documentation, dict)
        or not isinstance(documentation.get("official"), bool)
        or not isinstance(documentation.get("url"), str)
        or not documentation["url"].startswith(("https://", "http://"))
    ):
        raise RegistryValidationError(f"{tool_id}: documentation URL is required")
    if (
        not isinstance(definition["limitations"], list)
        or not definition["limitations"]
        or not all(isinstance(limit, str) and limit.strip() for limit in definition["limitations"])
    ):
        raise RegistryValidationError(f"{tool_id}: limitations must be a non-empty list")


def load_registry() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    """Load and validate the Phase 1 registry and all referenced definitions."""
    registry = load_yaml(REGISTRY_PATH)
    if not isinstance(registry.get("registry_version"), str) or not registry["registry_version"].strip():
        raise RegistryValidationError("Registry version is required")
    entries = registry.get("tools")
    if not isinstance(entries, list) or len(entries) != 3:
        raise RegistryValidationError("Registry must contain exactly three tools in Phase 1")
    ids = [entry.get("id") for entry in entries if isinstance(entry, dict)]
    if len(ids) != len(entries) or len(set(ids)) != len(ids):
        raise RegistryValidationError("Registry tool IDs must be unique")
    if set(ids) != EXPECTED_TOOL_IDS:
        raise RegistryValidationError(f"Phase 1 tool IDs must be {sorted(EXPECTED_TOOL_IDS)}")
    definitions: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str) or not entry["id"]:
            raise RegistryValidationError("Every registry entry needs a non-empty ID")
        definition_path = entry.get("definition")
        if not isinstance(definition_path, str) or not definition_path:
            raise RegistryValidationError(f"{entry['id']}: definition path is required")
        definition = load_yaml(TOOLS_DIR / definition_path)
        validate_definition(entry["id"], definition)
        definitions[entry["id"]] = definition
    return registry, definitions


def main() -> int:
    try:
        _, definitions = load_registry()
    except RegistryValidationError as exc:
        print(f"Tool Registry validation failed: {exc}")
        return 1
    print(f"Tool Registry validation passed ({len(definitions)} tool definitions).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
