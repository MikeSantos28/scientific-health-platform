"""Lightweight tests for the file-backed Dataset Registry v0.1."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from datasets.registry import DEFAULT_SCHEMA_PATH, DatasetRegistry, RegistryValidationError  # noqa: E402


def valid_dataset(dataset_id: str = "reads-001", status: str = "available") -> dict:
    return {
        "identity": {"id": dataset_id, "name": "Example paired-end reads"},
        "type": "sequencing_reads",
        "format": "fastq",
        "representations": [
            {"id": "read-1", "role": "read_1", "location": {"kind": "local", "uri": "data/R1.fastq.gz"}},
            {"id": "read-2", "role": "read_2", "location": {"kind": "local", "uri": "data/R2.fastq.gz"}}
        ],
        "lifecycle": {"status": status}
    }


class DatasetRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        root = Path(self.temporary_directory.name)
        self.registry_path = root / "datasets" / "registry.yaml"
        self.registry_path.parent.mkdir(parents=True)
        self.registry_path.write_text(json.dumps({"registry_version": "0.1", "datasets": []}), encoding="utf-8")
        self.registry = DatasetRegistry(self.registry_path, DEFAULT_SCHEMA_PATH)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def assert_invalid(self, dataset: dict, expected: str) -> None:
        with self.assertRaisesRegex(RegistryValidationError, expected):
            self.registry.validate(dataset)

    def test_valid_dataset(self) -> None:
        self.registry.validate(valid_dataset())

    def test_missing_identity_id(self) -> None:
        dataset = valid_dataset()
        del dataset["identity"]["id"]
        self.assert_invalid(dataset, "identity.*id")

    def test_missing_identity_name(self) -> None:
        dataset = valid_dataset()
        del dataset["identity"]["name"]
        self.assert_invalid(dataset, "identity.*name")

    def test_missing_type(self) -> None:
        dataset = valid_dataset()
        del dataset["type"]
        self.assert_invalid(dataset, "type")

    def test_missing_format(self) -> None:
        dataset = valid_dataset()
        del dataset["format"]
        self.assert_invalid(dataset, "format")

    def test_representation_missing_location(self) -> None:
        dataset = valid_dataset()
        del dataset["representations"][0]["location"]
        self.assert_invalid(dataset, "location")

    def test_location_missing_uri(self) -> None:
        dataset = valid_dataset()
        del dataset["representations"][0]["location"]["uri"]
        self.assert_invalid(dataset, "uri")

    def test_invalid_lifecycle_status(self) -> None:
        dataset = valid_dataset()
        dataset["lifecycle"]["status"] = "running"
        self.assert_invalid(dataset, "one of")

    def test_duplicate_representation_id(self) -> None:
        dataset = valid_dataset()
        dataset["representations"][1]["id"] = "read-1"
        self.assert_invalid(dataset, "unique")

    def test_registered_dataset_without_representation(self) -> None:
        dataset = valid_dataset(status="registered")
        dataset["representations"] = []
        self.registry.validate(dataset)

    def test_available_dataset_without_representation(self) -> None:
        dataset = valid_dataset(status="available")
        dataset["representations"] = []
        self.assert_invalid(dataset, "available Dataset")

    def test_parent_dataset_must_exist(self) -> None:
        dataset = valid_dataset()
        dataset["provenance"] = {"parents": ["unknown-parent"]}
        with self.assertRaisesRegex(RegistryValidationError, "Unknown parent"):
            self.registry.validate(dataset, known_dataset_ids=set())

    def test_register_and_retrieve_by_dataset_id(self) -> None:
        self.registry.register(valid_dataset())
        self.assertEqual(self.registry.get_dataset("reads-001")["identity"]["name"], "Example paired-end reads")

    def test_list_datasets(self) -> None:
        self.registry.register(valid_dataset("reads-001"))
        self.registry.register(valid_dataset("reads-002"))
        self.assertEqual([dataset["identity"]["id"] for dataset in self.registry.list_datasets()], ["reads-001", "reads-002"])

    def test_update_lifecycle_uses_schema_permitted_status(self) -> None:
        self.registry.register(valid_dataset("reads-001", status="registered"))
        updated = self.registry.update_lifecycle("reads-001", "available")
        self.assertEqual(updated["lifecycle"]["status"], "available")


if __name__ == "__main__":
    unittest.main()
