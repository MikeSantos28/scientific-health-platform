"""Lightweight contract tests for the declarative Phase 1 Tool Registry."""

from __future__ import annotations

import sys
from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "tools"))

from validate_registry import REGISTRY_PATH, TOOLS_DIR, load_registry  # noqa: E402


class ToolRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry, cls.definitions = load_registry()

    def test_registry_loads_successfully(self) -> None:
        self.assertTrue(REGISTRY_PATH.is_file())
        self.assertEqual(self.registry["registry_version"], "0.1")

    def test_exactly_three_tools_are_registered(self) -> None:
        self.assertEqual(len(self.registry["tools"]), 3)

    def test_fastp_can_be_located_by_id(self) -> None:
        self.assertIn("fastp", self.definitions)

    def test_megahit_can_be_located_by_id(self) -> None:
        self.assertIn("megahit", self.definitions)

    def test_diamond_can_be_located_by_id(self) -> None:
        self.assertIn("diamond", self.definitions)

    def test_every_registered_tool_has_inputs(self) -> None:
        self.assertTrue(all(definition["inputs"] for definition in self.definitions.values()))

    def test_every_registered_tool_has_outputs(self) -> None:
        self.assertTrue(all(definition["outputs"] for definition in self.definitions.values()))

    def test_every_registered_tool_has_execution_metadata(self) -> None:
        self.assertTrue(all(definition["execution"] for definition in self.definitions.values()))

    def test_no_duplicate_tool_ids_exist(self) -> None:
        ids = [entry["id"] for entry in self.registry["tools"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_all_referenced_definition_files_exist(self) -> None:
        for entry in self.registry["tools"]:
            self.assertTrue((TOOLS_DIR / entry["definition"]).is_file())


if __name__ == "__main__":
    unittest.main()
