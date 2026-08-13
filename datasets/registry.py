"""Dataset Registry v0.1.

This module manages declarative Dataset metadata only. It does not access data
locations, execute scientific software, or perform workflow orchestration.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA_PATH = PROJECT_ROOT / "schemas" / "dataset.schema.yaml"
DEFAULT_REGISTRY_PATH = Path(__file__).resolve().parent / "registry.yaml"


class RegistryValidationError(ValueError):
    """Raised when Dataset metadata violates a structural or semantic contract."""


def _load_mapping(path: Path) -> dict[str, Any]:
    """Load JSON-compatible YAML without adding a YAML dependency."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RegistryValidationError(f"Missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RegistryValidationError(f"Invalid JSON-compatible YAML in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise RegistryValidationError(f"Expected a mapping in {path}")
    return data


def _write_mapping(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


class DatasetRegistry:
    """File-backed catalog whose public records conform to Dataset Schema v0.1."""

    def __init__(self, registry_path: Path | str = DEFAULT_REGISTRY_PATH, schema_path: Path | str = DEFAULT_SCHEMA_PATH) -> None:
        self.registry_path = Path(registry_path)
        self.schema_path = Path(schema_path)
        self.schema = _load_mapping(self.schema_path)

    def _load_index(self) -> dict[str, Any]:
        index = _load_mapping(self.registry_path)
        if index.get("registry_version") != "0.1" or not isinstance(index.get("datasets"), list):
            raise RegistryValidationError("Dataset registry index must contain registry_version 0.1 and a datasets list")
        return index

    def _definition_path(self, relative_path: str) -> Path:
        path = self.registry_path.parent / relative_path
        if path.parent != (self.registry_path.parent / "definitions"):
            raise RegistryValidationError("Dataset definition must be stored directly under definitions/")
        return path

    def list_datasets(self) -> list[dict[str, Any]]:
        """Return all registered logical Datasets ordered as recorded in the index."""
        datasets: list[dict[str, Any]] = []
        for entry in self._load_index()["datasets"]:
            if not isinstance(entry, dict) or not isinstance(entry.get("id"), str) or not isinstance(entry.get("definition"), str):
                raise RegistryValidationError("Every registry entry requires id and definition")
            dataset = _load_mapping(self._definition_path(entry["definition"]))
            if dataset.get("identity", {}).get("id") != entry["id"]:
                raise RegistryValidationError(f"Registry entry {entry['id']} does not match its Dataset identity.id")
            datasets.append(dataset)
        return datasets

    def get_dataset(self, dataset_id: str) -> dict[str, Any] | None:
        """Return a Dataset by its stable identity.id, or None when it is unknown."""
        for dataset in self.list_datasets():
            if dataset["identity"]["id"] == dataset_id:
                return dataset
        return None

    def validate_structural(self, dataset: dict[str, Any]) -> None:
        """Validate Dataset structure using the checked-in Dataset Schema v0.1."""
        self._validate_schema(dataset, self.schema, self.schema, "$")

    def validate_semantic(self, dataset: dict[str, Any], known_dataset_ids: set[str] | None = None) -> None:
        """Validate rules intentionally outside the JSON Schema contract."""
        representations = dataset.get("representations", [])
        representation_ids = [representation.get("id") for representation in representations if isinstance(representation, dict)]
        if len(representation_ids) != len(set(representation_ids)):
            raise RegistryValidationError("representation.id values must be unique within a Dataset")
        if dataset.get("lifecycle", {}).get("status") == "available" and not representations:
            raise RegistryValidationError("An available Dataset must have at least one Representation")
        if known_dataset_ids is not None:
            parents = dataset.get("provenance", {}).get("parents", [])
            missing = [parent for parent in parents if parent not in known_dataset_ids]
            if missing:
                raise RegistryValidationError(f"Unknown parent Dataset IDs: {missing}")

    def validate(self, dataset: dict[str, Any], known_dataset_ids: set[str] | None = None) -> None:
        """Run structural validation followed by semantic validation."""
        self.validate_structural(dataset)
        self.validate_semantic(dataset, known_dataset_ids)

    def register(self, dataset: dict[str, Any]) -> dict[str, Any]:
        """Validate and persist one new Dataset definition in the file-backed registry."""
        index = self._load_index()
        existing_ids = {entry.get("id") for entry in index["datasets"] if isinstance(entry, dict)}
        self.validate(dataset, existing_ids)
        dataset_id = dataset["identity"]["id"]
        if dataset_id in existing_ids:
            raise RegistryValidationError(f"Dataset already registered: {dataset_id}")
        filename = f"{dataset_id}.yaml"
        definition_path = self._definition_path(f"definitions/{filename}")
        _write_mapping(definition_path, dataset)
        index["datasets"].append({"id": dataset_id, "definition": f"definitions/{filename}"})
        _write_mapping(self.registry_path, index)
        return deepcopy(dataset)

    def update_lifecycle(self, dataset_id: str, status: str) -> dict[str, Any]:
        """Set a schema-permitted lifecycle status and revalidate the Dataset.

        Dataset Schema v0.1 defines allowed states but no transition graph;
        consequently this method does not invent transition restrictions.
        """
        dataset = self.get_dataset(dataset_id)
        if dataset is None:
            raise RegistryValidationError(f"Unknown Dataset ID: {dataset_id}")
        updated = deepcopy(dataset)
        updated["lifecycle"]["status"] = status
        known_ids = {item["identity"]["id"] for item in self.list_datasets()}
        self.validate(updated, known_ids)
        entry = next(entry for entry in self._load_index()["datasets"] if entry["id"] == dataset_id)
        _write_mapping(self._definition_path(entry["definition"]), updated)
        return updated

    def _validate_schema(self, value: Any, schema: dict[str, Any], root_schema: dict[str, Any], path: str) -> None:
        if "$ref" in schema:
            reference = schema["$ref"]
            if not reference.startswith("#/$defs/"):
                raise RegistryValidationError(f"Unsupported schema reference at {path}: {reference}")
            definition_name = reference.removeprefix("#/$defs/")
            self._validate_schema(value, root_schema["$defs"][definition_name], root_schema, path)
            return
        if "oneOf" in schema:
            matches = 0
            for candidate in schema["oneOf"]:
                try:
                    self._validate_schema(value, candidate, root_schema, path)
                    matches += 1
                except RegistryValidationError:
                    pass
            if matches != 1:
                raise RegistryValidationError(f"{path}: value must match exactly one permitted schema")
            return
        expected_type = schema.get("type")
        type_checks = {"object": lambda item: isinstance(item, dict), "array": lambda item: isinstance(item, list), "string": lambda item: isinstance(item, str), "integer": lambda item: isinstance(item, int) and not isinstance(item, bool), "boolean": lambda item: isinstance(item, bool), "number": lambda item: isinstance(item, (int, float)) and not isinstance(item, bool), "null": lambda item: item is None}
        if expected_type and not type_checks[expected_type](value):
            raise RegistryValidationError(f"{path}: expected {expected_type}")
        if "enum" in schema and value not in schema["enum"]:
            raise RegistryValidationError(f"{path}: value must be one of {schema['enum']}")
        if isinstance(value, str) and len(value) < schema.get("minLength", 0):
            raise RegistryValidationError(f"{path}: string must not be empty")
        if isinstance(value, dict):
            for required_property in schema.get("required", []):
                if required_property not in value:
                    raise RegistryValidationError(f"{path}: missing required property {required_property}")
            properties = schema.get("properties", {})
            if schema.get("additionalProperties") is False:
                unexpected = set(value) - set(properties)
                if unexpected:
                    raise RegistryValidationError(f"{path}: unsupported properties {sorted(unexpected)}")
            for property_name, property_value in value.items():
                if property_name in properties:
                    self._validate_schema(property_value, properties[property_name], root_schema, f"{path}.{property_name}")
        if isinstance(value, list):
            for index, item in enumerate(value):
                self._validate_schema(item, schema.get("items", {}), root_schema, f"{path}[{index}]")
