"""Repo introspection: build folder-level facts for the Z3 model.

Heuristics here are deliberately cheap. Anything genuinely uncertain is
tagged `confidence="low"` so the solver weights it conservatively.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from ..manifest.schema import MANIFEST_FILE_NAMES

# Hints that a folder likely holds raw lead/contact data (PII).
_PII_HINTS: tuple[str, ...] = (
    "lead",
    "leads",
    "contact",
    "contacts",
    "prospect",
    "pii",
    "personal",
    "email_list",
    "subscribers",
)

# Hints that a folder is a derivation/cache/output.
_DERIVED_HINTS: tuple[str, ...] = (
    "output",
    "outputs",
    "cache",
    "generated",
    "derived",
    "build",
    "dist",
    "__pycache__",
    "results",
    ".next",
    "node_modules",
)

# Hints of secrets at rest.
_SECRET_FILE_PATTERNS = (
    re.compile(r"^\.env(\..+)?$"),
    re.compile(r"\.pem$"),
    re.compile(r"\.key$"),
    re.compile(r"credentials.*\.json$"),
    re.compile(r"secrets?\.ya?ml$"),
)

# Hints of canonical / source-of-truth assets.
_CANONICAL_HINTS: tuple[str, ...] = (
    "master",
    "canonical",
    "source",
    "golden",
    "registry",
    "catalog",
)

# Hints of archive / retire / legacy.
_ARCHIVE_HINTS: tuple[str, ...] = (
    "archive",
    "archived",
    "archived_files",
    "legacy",
    "deprecated",
    "old",
    "backup",
    "backups",
)

# Scopes used for IC1 (canonicality): per-scope, exactly one source-of-truth.
# v0.1 bootstrap scopes for K=outbound-pipeline.
SCOPES: tuple[str, ...] = (
    "lead_records",
    "suppression_list",
    "sequence_state",
    "consent_record",
    "delivery_proof",
)

_SCOPE_HINTS: dict[str, tuple[str, ...]] = {
    "lead_records": ("lead", "leads", "contact", "contacts", "prospect"),
    "suppression_list": ("suppression", "unsubscribe", "do_not_contact", "dnc"),
    "sequence_state": ("sequence", "sequences", "campaign", "smartlead", "cohort"),
    "consent_record": ("consent", "opt_in", "double_opt"),
    "delivery_proof": ("delivery", "bounce", "sent", "outbound_log"),
}

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
        ".next",
        ".cache",
    }
)


@dataclass
class FolderFact:
    """Compact, pickleable view of one folder. Inputs into the Z3 model."""

    path: Path
    rel_path: str  # POSIX-style, repo-relative
    depth: int
    file_count: int
    bytes: int

    has_manifest: bool
    has_secret_at_rest: bool
    has_pii_signal: bool
    looks_derived: bool
    looks_archived: bool
    looks_canonical: bool

    scopes_matched: tuple[str, ...] = field(default_factory=tuple)
    # `True` when the folder is "stable enough" that IC3 expects a manifest:
    # non-empty, not noise, not a leaf in a deep ephemeral tree.
    is_stable_boundary: bool = False


def _has_manifest(folder: Path) -> bool:
    return any((folder / name).is_file() for name in MANIFEST_FILE_NAMES)


def _name_matches(name: str, hints: tuple[str, ...]) -> bool:
    lower = name.lower()
    return any(h in lower for h in hints)


def _has_secret_file(folder: Path) -> bool:
    try:
        entries = list(folder.iterdir())
    except OSError:
        return False
    for entry in entries:
        if not entry.is_file():
            continue
        for pat in _SECRET_FILE_PATTERNS:
            if pat.search(entry.name):
                return True
    return False


def _folder_stats(folder: Path) -> tuple[int, int]:
    n = 0
    total = 0
    try:
        for entry in folder.iterdir():
            if entry.is_file():
                n += 1
                try:
                    total += entry.stat().st_size
                except OSError:
                    pass
    except OSError:
        return 0, 0
    return n, total


def _scopes_for(name: str) -> tuple[str, ...]:
    lower = name.lower()
    matched: list[str] = []
    for scope, hints in _SCOPE_HINTS.items():
        if any(h in lower for h in hints):
            matched.append(scope)
    return tuple(matched)


def introspect_repo(
    root: Path,
    min_files_for_stable_boundary: int = 3,
) -> list[FolderFact]:
    """Walk `root`, build a FolderFact per directory.

    Skips noise dirs (.git, venvs, build outputs of common toolchains).
    A folder is `is_stable_boundary` if it holds >= min_files at depth >= 1.
    """
    root = root.resolve()
    facts: list[FolderFact] = []

    for folder in _walk(root):
        rel = folder.relative_to(root)
        rel_posix = rel.as_posix() if str(rel) != "." else ""
        name = folder.name or root.name
        depth = len(rel.parts)
        file_count, byte_total = _folder_stats(folder)

        fact = FolderFact(
            path=folder,
            rel_path=rel_posix,
            depth=depth,
            file_count=file_count,
            bytes=byte_total,
            has_manifest=_has_manifest(folder),
            has_secret_at_rest=_has_secret_file(folder),
            has_pii_signal=_name_matches(name, _PII_HINTS),
            looks_derived=_name_matches(name, _DERIVED_HINTS),
            looks_archived=_name_matches(name, _ARCHIVE_HINTS),
            looks_canonical=_name_matches(name, _CANONICAL_HINTS),
            scopes_matched=_scopes_for(name),
        )
        fact.is_stable_boundary = (
            depth >= 1 and file_count >= min_files_for_stable_boundary and not fact.looks_derived
        )
        facts.append(fact)

    return facts


def _walk(root: Path):
    yield root
    for path in root.rglob("*"):
        if not path.is_dir():
            continue
        if any(part in _SKIP_DIRS for part in path.parts):
            continue
        yield path
