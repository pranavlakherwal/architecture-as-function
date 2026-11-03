"""Stub-manifest generator for A* (Architecture as a Function).

Walks a target repo, finds non-leaf folders missing `.manifest.yaml`, and
writes a pre-filled stub manifest that:
  - Satisfies the IC3 folder-as-contract schema mechanically
    (a_star/manifest/schema.py MANIFEST_SCHEMA)
  - Is clearly marked as REVIEW_REQUIRED via YAML header comment + an
    explicit owner sentinel + `lifecycle_status: bootstrap`
  - Inherits k_class / lifecycle / owner from the nearest parent manifest
    when one is present

Usage:
    python -m tools.stub_manifest --root /path/to/repo            # dry-run
    python -m tools.stub_manifest --root /path/to/repo --apply
    python -m tools.stub_manifest --root /path/to/repo --apply \
        --report /tmp/stub_report.json

Schema note:
  The A* manifest schema has `additionalProperties: False`, so extra
  fields like `review_required` / `generated_by` cannot live inside the
  YAML body. We surface them as a YAML header comment block and encode
  the review intent via `lifecycle_status: bootstrap` + a sentinel
  `owner: "unknown (stub_manifest.py - review_required)"`.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML required: pip install pyyaml") from exc


# Folder names to skip entirely (never walk into).
SKIP_DIRS: frozenset[str] = frozenset(
    {
        ".git",
        "__pycache__",
        "node_modules",
        ".venv",
        "venv",
        "dist",
        "build",
        ".next",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".idea",
        ".vscode",
        ".cache",
        # archived folders (per spec)
        "archive",
        "archived",
        "archived_files",
    }
)

# Filenames the A* validator recognises as a manifest.
MANIFEST_FILE_NAMES: tuple[str, ...] = (
    ".manifest.yaml",
    ".manifest.yml",
    ".manifest.json",
    "MANIFEST.yaml",
    "MANIFEST.yml",
    "MANIFEST.json",
)

DEFAULT_MANIFEST_NAME = ".manifest.yaml"

# Extension -> rough artifact-type label used during purpose inference.
_EXT_LABELS: dict[str, str] = {
    ".py": "python",
    ".pyi": "python",
    ".ipynb": "notebook",
    ".js": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".jsx": "javascript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".rb": "ruby",
    ".sh": "shell",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".json": "json",
    ".toml": "config",
    ".ini": "config",
    ".md": "markdown",
    ".rst": "docs",
    ".txt": "text",
    ".csv": "dataset",
    ".tsv": "dataset",
    ".parquet": "dataset",
    ".sql": "sql",
    ".html": "html",
    ".css": "css",
    ".scss": "css",
    ".sqlite": "database",
    ".db": "database",
    ".pdf": "pdf",
    ".docx": "document",
    ".xlsx": "spreadsheet",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".svg": "image",
}

_TEST_HINTS = ("test_", "_test.")


@dataclass
class StubResult:
    """One folder's outcome."""

    folder: Path
    rel: str
    action: str  # "wrote" | "would_write" | "skipped"
    reason: str = ""
    inherited_from: str | None = None
    purpose: str = ""


@dataclass
class StubReport:
    root: Path
    apply: bool
    results: list[StubResult] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        by_action: dict[str, int] = {}
        for r in self.results:
            by_action[r.action] = by_action.get(r.action, 0) + 1
        return {
            "root": str(self.root),
            "apply": self.apply,
            "totals": by_action,
            "results": [
                {
                    "folder": str(r.folder),
                    "rel": r.rel,
                    "action": r.action,
                    "reason": r.reason,
                    "inherited_from": r.inherited_from,
                    "purpose": r.purpose,
                }
                for r in self.results
            ],
        }


# ---------------------------------------------------------------------------
# Inference helpers
# ---------------------------------------------------------------------------


def _has_manifest(folder: Path) -> bool:
    return any((folder / n).is_file() for n in MANIFEST_FILE_NAMES)


def _is_skippable(folder: Path, root: Path) -> bool:
    try:
        rel = folder.relative_to(root)
    except ValueError:
        return True
    return any(part in SKIP_DIRS for part in rel.parts)


def _direct_children(folder: Path) -> tuple[list[Path], list[Path]]:
    """Return (files, subdirs) for a folder, swallowing permission errors."""
    files: list[Path] = []
    dirs: list[Path] = []
    try:
        for entry in folder.iterdir():
            if entry.is_file():
                files.append(entry)
            elif entry.is_dir():
                dirs.append(entry)
    except OSError:
        pass
    return files, dirs


def infer_purpose(folder: Path, files: list[Path], subdirs: list[Path]) -> str:
    """Best-guess one-line purpose from folder name + child file extensions."""
    name = folder.name or "root"

    ext_counts: dict[str, int] = {}
    has_tests = False
    for f in files:
        ext = f.suffix.lower()
        if ext:
            ext_counts[ext] = ext_counts.get(ext, 0) + 1
        lower = f.name.lower()
        if any(h in lower for h in _TEST_HINTS):
            has_tests = True

    if not ext_counts and not subdirs:
        return f"{name} (empty folder; review whether it should exist)"

    # Pick top-2 extensions by count.
    top = sorted(ext_counts.items(), key=lambda kv: -kv[1])[:2]
    labels: list[str] = []
    for ext, _count in top:
        label = _EXT_LABELS.get(ext, ext.lstrip(".") or "binary")
        if label not in labels:
            labels.append(label)

    if not labels and subdirs:
        return f"{name} (container of {len(subdirs)} subfolder(s); review)"

    body = "+".join(labels) if labels else "mixed"
    descriptor = f"{body} module"
    if has_tests:
        descriptor += " with tests"
    if subdirs:
        descriptor += f" ({len(subdirs)} subfolder(s))"

    return f"{name}: {descriptor}"


def infer_allowed_types(files: list[Path]) -> list[str]:
    """Concrete artifact types found in this folder, deduped."""
    types: list[str] = []
    seen: set[str] = set()
    for f in files:
        label = _EXT_LABELS.get(f.suffix.lower())
        if label and label not in seen:
            seen.add(label)
            types.append(label)
    if not types:
        types = ["unknown"]
    return types


# ---------------------------------------------------------------------------
# Parent-manifest inheritance
# ---------------------------------------------------------------------------


def load_nearest_parent_manifest(folder: Path, root: Path) -> tuple[dict[str, Any] | None, Path | None]:
    """Walk up from `folder` to `root` and return the first manifest found.

    Skips the folder itself; we want the *parent* contract.
    """
    cur = folder.parent
    while True:
        for name in MANIFEST_FILE_NAMES:
            candidate = cur / name
            if candidate.is_file():
                try:
                    if candidate.suffix in (".yaml", ".yml"):
                        data = yaml.safe_load(candidate.read_text(encoding="utf-8")) or {}
                    else:
                        data = json.loads(candidate.read_text(encoding="utf-8"))
                    return data, candidate
                except Exception:
                    return None, candidate
        if cur == root or cur.parent == cur:
            return None, None
        cur = cur.parent


# ---------------------------------------------------------------------------
# Manifest construction
# ---------------------------------------------------------------------------


def build_stub(
    folder: Path,
    root: Path,
    files: list[Path],
    subdirs: list[Path],
    parent: dict[str, Any] | None,
) -> dict[str, Any]:
    """Build a schema-conformant stub manifest dict for `folder`."""
    purpose = infer_purpose(folder, files, subdirs)

    parent = parent or {}
    inherited_owner = parent.get("owner")
    inherited_lifecycle = parent.get("lifecycle_status")
    inherited_k_class = parent.get("k_class")
    inherited_review = parent.get("review_cadence")

    # Owner: prefer parent; otherwise sentinel that screams "review me".
    owner = inherited_owner or "unknown (stub_manifest.py - review_required)"

    # Lifecycle: always start as bootstrap for stubs so the file is not
    # mistaken for a hand-curated production manifest.
    lifecycle = "bootstrap"

    manifest: dict[str, Any] = {
        "manifest_version": "1",
        "scope": purpose,
        "exclusions": [],
        "allowed_artifact_types": infer_allowed_types(files),
        "owner": owner,
        "lifecycle_status": lifecycle,
        "required_metadata": [],
        "outbound_relations": [],
        "review_cadence": inherited_review or "weekly",
        "retention": {
            "class": "active",
            "policy": "none",
            "window": "indefinite",
        },
        "source_of_truth": False,
    }
    if inherited_k_class:
        manifest["k_class"] = inherited_k_class
    else:
        manifest["k_class"] = "unclassified"

    return manifest


def render_manifest_yaml(manifest: dict[str, Any], header: dict[str, Any]) -> str:
    """Render manifest with a YAML comment header carrying generator metadata."""
    header_lines = [
        "# AUTO-GENERATED STUB MANIFEST - review_required: true",
        f"# generated_by: {header['generated_by']}",
        f"# generated_at: {header['generated_at']}",
        f"# inherited_from: {header.get('inherited_from') or 'none'}",
        "# Edit this file to replace stub values with real contract terms,",
        "# then flip lifecycle_status from 'bootstrap' to 'production' and",
        "# replace the owner sentinel with a real human or team name.",
        "",
    ]
    body = yaml.safe_dump(manifest, sort_keys=False, default_flow_style=False)
    return "\n".join(header_lines) + body


# ---------------------------------------------------------------------------
# Core walk
# ---------------------------------------------------------------------------


def generate(
    root: Path,
    apply: bool = False,
    today: str | None = None,
) -> StubReport:
    """Walk `root`; write or simulate writes of stub manifests."""
    root = root.resolve()
    if not root.is_dir():
        raise SystemExit(f"--root must be an existing directory: {root}")

    today = today or _dt.date.today().isoformat()
    report = StubReport(root=root, apply=apply)

    # We intentionally do NOT generate a manifest for the repo root if it
    # already has one (typical case). If root lacks a manifest, we treat it
    # like any other folder.
    for folder in _walk(root):
        rel = folder.relative_to(root).as_posix() or "."
        if _is_skippable(folder, root):
            report.results.append(
                StubResult(
                    folder=folder,
                    rel=rel,
                    action="skipped",
                    reason="ignore_pattern",
                )
            )
            continue

        if _has_manifest(folder):
            report.results.append(
                StubResult(
                    folder=folder,
                    rel=rel,
                    action="skipped",
                    reason="manifest_exists",
                )
            )
            continue

        files, subdirs = _direct_children(folder)

        # Leaf-and-empty: a folder with neither files nor subdirs is not a
        # useful target. The spec says "non-leaf"; we treat any folder with
        # zero direct files AND zero subdirs as a leaf to skip.
        if not files and not subdirs:
            report.results.append(
                StubResult(
                    folder=folder,
                    rel=rel,
                    action="skipped",
                    reason="empty_leaf",
                )
            )
            continue

        parent, parent_path = load_nearest_parent_manifest(folder, root)
        manifest = build_stub(folder, root, files, subdirs, parent)
        header = {
            "generated_by": "stub_manifest.py",
            "generated_at": today,
            "inherited_from": (str(parent_path.relative_to(root)) if parent_path else None),
        }
        text = render_manifest_yaml(manifest, header)

        target = folder / DEFAULT_MANIFEST_NAME
        if apply:
            target.write_text(text, encoding="utf-8")
            action = "wrote"
        else:
            action = "would_write"

        report.results.append(
            StubResult(
                folder=folder,
                rel=rel,
                action=action,
                inherited_from=str(parent_path) if parent_path else None,
                purpose=manifest["scope"],
            )
        )

    return report


def _walk(root: Path):
    """Yield root and every non-skipped subdirectory."""
    yield root
    for path in sorted(root.rglob("*")):
        if not path.is_dir():
            continue
        if _is_skippable(path, root):
            continue
        yield path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _print_summary(report: StubReport) -> None:
    totals: dict[str, int] = {}
    for r in report.results:
        totals[r.action] = totals.get(r.action, 0) + 1
    mode = "APPLY" if report.apply else "DRY-RUN"
    print(f"[{mode}] root={report.root}")
    for action in ("wrote", "would_write", "skipped"):
        if action in totals:
            print(f"  {action:>11}: {totals[action]}")
    if not report.apply:
        # Show first 10 would_writes so the user sees what's coming.
        previews = [r for r in report.results if r.action == "would_write"][:10]
        for r in previews:
            print(f"    + {r.rel}  ({r.purpose})")
        more = sum(1 for r in report.results if r.action == "would_write") - len(previews)
        if more > 0:
            print(f"    ... and {more} more")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="A* stub-manifest generator (IC3 satisfier, review_required).",
    )
    parser.add_argument("--root", required=True, type=Path, help="Repo root to walk.")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually write manifests. Default is dry-run.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Explicit dry-run flag (default if --apply not passed).",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Write a JSON summary report to this path.",
    )
    args = parser.parse_args(argv)

    if args.apply and args.dry_run:
        print("error: cannot pass both --apply and --dry-run", file=sys.stderr)
        return 2

    apply = bool(args.apply)
    report = generate(args.root, apply=apply)
    _print_summary(report)

    if args.report is not None:
        args.report.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
        print(f"wrote report -> {args.report}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
