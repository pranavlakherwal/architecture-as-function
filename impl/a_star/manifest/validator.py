"""Manifest validator + repo scanner.

CI usage:
    python -m a_star.manifest.validator /path/to/repo

Exits non-zero if any violations are found. Designed to drop into pre-commit
or GitHub Actions.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .schema import MANIFEST_FILE_NAMES, MANIFEST_SCHEMA

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover
    Draft202012Validator = None


# Folders that should be skipped during scans (noise, not first-class folders).
_SKIP_DIRS: frozenset[str] = frozenset(
    {
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".idea",
        ".vscode",
        "dist",
        "build",
        ".next",
        ".cache",
    }
)


@dataclass
class ManifestViolation:
    folder: Path
    code: str
    message: str

    def __str__(self) -> str:
        return f"[{self.code}] {self.folder}: {self.message}"


@dataclass
class ValidationResult:
    folder: Path
    manifest_path: Path | None
    manifest: dict[str, Any] | None
    violations: list[ManifestViolation] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.violations


def _load_manifest(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix in (".yaml", ".yml") or path.name.endswith((".yaml", ".yml")):
        if yaml is None:
            raise RuntimeError("PyYAML required for YAML manifests")
        return yaml.safe_load(text) or {}
    return json.loads(text)


def _find_manifest(folder: Path) -> Path | None:
    for name in MANIFEST_FILE_NAMES:
        candidate = folder / name
        if candidate.is_file():
            return candidate
    return None


def validate_manifest(folder: Path) -> ValidationResult:
    """Validate the manifest for a single folder.

    Returns a ValidationResult. A folder without a manifest yields a result
    with `manifest_path=None` and no violations (callers decide if missing
    manifests are violations based on policy).
    """
    manifest_path = _find_manifest(folder)
    if manifest_path is None:
        return ValidationResult(folder=folder, manifest_path=None, manifest=None)

    try:
        manifest = _load_manifest(manifest_path)
    except Exception as exc:
        return ValidationResult(
            folder=folder,
            manifest_path=manifest_path,
            manifest=None,
            violations=[
                ManifestViolation(
                    folder=folder,
                    code="MANIFEST_PARSE_ERROR",
                    message=f"could not parse {manifest_path.name}: {exc}",
                )
            ],
        )

    violations: list[ManifestViolation] = []
    if Draft202012Validator is None:
        violations.append(
            ManifestViolation(
                folder=folder,
                code="MISSING_DEPENDENCY",
                message="jsonschema not installed; install to enable schema validation",
            )
        )
    else:
        validator = Draft202012Validator(MANIFEST_SCHEMA)
        for err in sorted(validator.iter_errors(manifest), key=lambda e: list(e.path)):
            path = ".".join(str(p) for p in err.absolute_path) or "<root>"
            violations.append(
                ManifestViolation(
                    folder=folder,
                    code="SCHEMA_VIOLATION",
                    message=f"{path}: {err.message}",
                )
            )

    return ValidationResult(
        folder=folder,
        manifest_path=manifest_path,
        manifest=manifest,
        violations=violations,
    )


def scan_repo(
    root: Path,
    require_manifest_at_depth: int | None = None,
) -> list[ValidationResult]:
    """Walk a repo, validating every folder that has a manifest.

    If `require_manifest_at_depth` is set, folders at that depth from `root`
    that lack a manifest will receive a MISSING_MANIFEST violation. Use
    `None` (default) to be advisory only: validate present manifests, ignore
    absent ones.
    """
    root = root.resolve()
    results: list[ValidationResult] = []

    for folder in _walk(root):
        result = validate_manifest(folder)
        if result.manifest_path is None and require_manifest_at_depth is not None:
            depth = len(folder.relative_to(root).parts)
            if depth == require_manifest_at_depth:
                result.violations.append(
                    ManifestViolation(
                        folder=folder,
                        code="MISSING_MANIFEST",
                        message=f"no manifest file at depth {depth} (expected one of {MANIFEST_FILE_NAMES})",
                    )
                )
        if result.manifest_path is not None or result.violations:
            results.append(result)

    return results


def _walk(root: Path):
    """Yield folders under root, skipping noise dirs."""
    yield root
    for path in root.rglob("*"):
        if not path.is_dir():
            continue
        if any(part in _SKIP_DIRS for part in path.parts):
            continue
        yield path


def _main() -> int:
    parser = argparse.ArgumentParser(
        description="A* folder-as-contract manifest validator (IC2 + IC3)."
    )
    parser.add_argument("root", type=Path, help="Repo root to scan.")
    parser.add_argument(
        "--require-depth",
        type=int,
        default=None,
        help="If set, folders at this depth without a manifest are flagged.",
    )
    args = parser.parse_args()

    results = scan_repo(args.root, require_manifest_at_depth=args.require_depth)
    n_violations = 0
    for r in results:
        if r.violations:
            for v in r.violations:
                print(v, file=sys.stderr)
                n_violations += 1
        else:
            print(f"OK  {r.folder}")

    if n_violations:
        print(f"\n{n_violations} violation(s) found.", file=sys.stderr)
        return 1
    print(f"\nAll manifests valid ({len(results)} folder(s) with manifests).")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
