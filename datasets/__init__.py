"""Lightweight, file-backed Dataset Registry for declarative Dataset metadata."""

from .registry import DatasetRegistry, RegistryValidationError

__all__ = ["DatasetRegistry", "RegistryValidationError"]
