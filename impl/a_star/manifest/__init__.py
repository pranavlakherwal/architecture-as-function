"""Manifest schema + folder-as-contract validator.

IC3 in A_STAR_v0.md §3: every stable folder that functions as a navigation,
ownership, lifecycle, or execution boundary declares a manifest.

Schema lives in `schema.py`. Validator lives in `validator.py`.
"""

from .schema import MANIFEST_SCHEMA, MANIFEST_FILE_NAMES
from .validator import (
    ManifestViolation,
    ValidationResult,
    validate_manifest,
    scan_repo,
)

__all__ = [
    "MANIFEST_SCHEMA",
    "MANIFEST_FILE_NAMES",
    "ManifestViolation",
    "ValidationResult",
    "validate_manifest",
    "scan_repo",
]
