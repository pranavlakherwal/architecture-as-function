"""Passive C_core measurement instrument.

Implements §11 measurement-gap row: per axis declares unit, range,
normalization, source, confidence, owner, update cadence.

Honesty principle: where a defensible proxy does not exist, the axis
returns `confidence="low"` with a `missing` note. We never invent a
number to hit a schema.

Sources used (all cheap, all passive):
  - filesystem walk for c_storage, c_find size hints
  - git log for c_modify (churn) and c_drift (entropy delta proxy)
  - dead-link + orphan scan for c_loss
  - cache/derived inventory for c_derive
  - c_money requires external billing input and is left as low-confidence
    placeholder (provided as `external_inputs` kwarg)
"""

from __future__ import annotations

import math
import re
import subprocess
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

Confidence = Literal["high", "medium", "low"]

# Runner version. Bump on ANY axis-formula change. Determinism contract:
# given identical inputs and runner_version, every axis value MUST be
# bit-identical across runs. See impl/bench/quality/test_determinism.py.
RUNNER_VERSION = "0.2.1"

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


@dataclass(frozen=True)
class AxisSpec:
    """§11 measurement metadata for a single C_core axis."""

    name: str
    unit: str
    range: str
    normalization: str
    source: str
    default_confidence: Confidence
    owner: str
    update_cadence: str


AXIS_SPECS: dict[str, AxisSpec] = {
    "c_find": AxisSpec(
        name="c_find",
        unit="seconds (estimated)",
        range="[0, +inf)",
        normalization="log(1+x) capped at 99th percentile",
        source="fs depth + filename entropy (Sinha 2023 task instrumentation if available)",
        default_confidence="medium",
        owner="architecture",
        update_cadence="weekly",
    ),
    "c_modify": AxisSpec(
        name="c_modify",
        unit="commits-per-change (proxy)",
        range="[0, +inf)",
        normalization="z-score over repo history",
        source="git log churn + change-coupling",
        default_confidence="medium",
        owner="architecture",
        update_cadence="per-commit",
    ),
    "c_storage": AxisSpec(
        name="c_storage",
        unit="bytes",
        range="[0, +inf)",
        normalization="log(1+bytes)",
        source="filesystem walk",
        default_confidence="high",
        owner="ops",
        update_cadence="daily",
    ),
    "c_money": AxisSpec(
        name="c_money",
        unit="USD per month",
        range="[0, +inf)",
        normalization="log(1+usd)",
        source="external billing input (cloud + API spend)",
        default_confidence="low",
        owner="ops",
        update_cadence="monthly",
    ),
    "c_drift": AxisSpec(
        name="c_drift",
        unit="entropy-delta per unit time",
        range="[0, 1]",
        normalization="bounded entropy over windowed git history",
        source="Mannan structural entropy proxy (extension distribution drift)",
        default_confidence="low",
        owner="architecture",
        update_cadence="weekly",
    ),
    "c_loss": AxisSpec(
        name="c_loss",
        unit="orphan/dead-link count",
        range="[0, +inf)",
        normalization="per 1k artifacts",
        source="dead-link + orphan scan (FAIR-style ALE upstream)",
        default_confidence="medium",
        owner="architecture",
        update_cadence="weekly",
    ),
    "c_derive": AxisSpec(
        name="c_derive",
        unit="derivation_count",
        range="[0, +inf)",
        normalization="per source artifact",
        source="cache/derived inventory (INVENT-tier per §13)",
        default_confidence="low",
        owner="architecture",
        update_cadence="weekly",
    ),
}


@dataclass
class Measurement:
    axis: str
    value: float
    confidence: Confidence
    notes: list[str] = field(default_factory=list)


@dataclass
class CoreVector:
    repo: Path
    measurements: dict[str, Measurement]

    def as_dict(self) -> dict[str, dict]:
        return {
            axis: {
                "value": m.value,
                "confidence": m.confidence,
                "notes": m.notes,
            }
            for axis, m in self.measurements.items()
        }

    def values_only(self) -> dict[str, float]:
        return {axis: m.value for axis, m in self.measurements.items()}


# ---- Per-axis measurement primitives ----------------------------------------


def _walk_files(root: Path):
    """Deterministic file walk: sorted, depth-first, skip dirs filtered.

    rglob() iteration order is OS-dependent; we materialize + sort so that
    every dict/Counter insertion happens in canonical order. This is what
    makes intermediate_metrics bit-identical across runs (test_determinism).
    """
    paths = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in _SKIP_DIRS for part in path.parts):
            continue
        paths.append(path)
    paths.sort()
    for p in paths:
        yield p


def _git(cmd: list[str], cwd: Path) -> str | None:
    try:
        out = subprocess.run(
            ["git", *cmd],
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return out.stdout
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return None


def prefix_key(name: str) -> str:
    """The first four letters of a file name before its first dot or underscore.

    Sibling files that share this key read as look-alikes to a person scanning a folder.
    The report uses the same key, so the fix it names matches the reading.
    """
    return name.split(".")[0].split("_")[0][:4]


def folder_distinctness(names: list[str]) -> float:
    """How distinct the leading tokens of sibling file names are, 0 to 1. One file scores 1."""
    if len(names) <= 1:
        return 1.0
    ctr = Counter(prefix_key(n) for n in names)
    total = sum(ctr.values())
    h = -sum((c / total) * math.log2(c / total) for c in ctr.values())
    max_h = math.log2(len(ctr)) if len(ctr) > 1 else 1.0
    return h / max_h if max_h > 0 else 0.0


def measure_c_find(root: Path) -> Measurement:
    """Proxy: mean folder depth + filename-entropy-per-folder.

    Lower is better. Combines structural depth (how deep you have to click)
    with intra-folder discriminability (how distinct sibling filenames are).
    """
    depths: list[int] = []
    by_folder: dict[Path, list[str]] = {}
    for f in _walk_files(root):
        rel = f.relative_to(root)
        depths.append(len(rel.parts) - 1)
        by_folder.setdefault(f.parent, []).append(f.name)

    if not depths:
        return Measurement(axis="c_find", value=0.0, confidence="low", notes=["empty repo"])

    mean_depth = sum(depths) / len(depths)

    # Average uniqueness of leading filename token per folder.
    distinctness_scores: list[float] = [folder_distinctness(names) for names in by_folder.values()]

    avg_distinct = sum(distinctness_scores) / len(distinctness_scores)
    # c_find proxy: depth penalizes, distinctness rewards.
    value = mean_depth * (1.0 + (1.0 - avg_distinct))
    return Measurement(
        axis="c_find",
        value=round(value, 3),
        confidence="medium",
        notes=[
            f"mean_depth={mean_depth:.2f}",
            f"avg_prefix_distinctness={avg_distinct:.2f}",
        ],
    )


def touch_counts(root: Path, until: str | None = None) -> Counter | None:
    """How many commits touched each file in the 365 day window ending `until`.

    Returns None when git is unavailable or `root` is not a repository.
    The report reads the same counter, so the files it names are the ones the reading counted.
    """
    cmd = ["log", "--since=365.days"]
    if until is not None:
        cmd.append(f"--until={until}")
    cmd.extend(["--name-only", "--pretty=format:"])
    out = _git(cmd, root)
    if out is None:
        return None
    return Counter(line.strip() for line in out.splitlines() if line.strip())


def measure_c_modify(root: Path, until: str | None = None) -> Measurement:
    """Proxy: commits per touched file over the 365d window ending `until`.

    `until` is an ISO-8601 timestamp (UTC). If None, `git log` defaults to
    HEAD's date semantics. For deterministic bench measurements, pass the
    record's `measured_at`; this freezes the window relative to a logical
    clock rather than wall-clock.
    """
    ctr = touch_counts(root, until=until)
    if ctr is None:
        return Measurement(
            axis="c_modify",
            value=0.0,
            confidence="low",
            notes=["git unavailable or not a repo"],
        )

    if not ctr:
        return Measurement(
            axis="c_modify",
            value=0.0,
            confidence="low",
            notes=["no commits in last 365d"],
        )

    avg_churn = sum(ctr.values()) / len(ctr)
    # Higher churn-per-file = harder to modify safely (proxy).
    return Measurement(
        axis="c_modify",
        value=round(avg_churn, 3),
        confidence="medium",
        notes=[
            f"touched_files={len(ctr)}",
            f"total_touches={sum(ctr.values())}",
        ],
    )


def measure_c_storage(root: Path) -> Measurement:
    total = 0
    n = 0
    for f in _walk_files(root):
        try:
            total += f.stat().st_size
        except OSError:
            continue
        n += 1
    return Measurement(
        axis="c_storage",
        value=float(total),
        confidence="high",
        notes=[f"bytes_total={total}", f"file_count={n}"],
    )


def measure_c_money(root: Path, monthly_usd: float | None = None) -> Measurement:
    if monthly_usd is None:
        return Measurement(
            axis="c_money",
            value=0.0,
            confidence="low",
            notes=["no external billing input provided"],
        )
    return Measurement(
        axis="c_money",
        value=float(monthly_usd),
        confidence="high",
        notes=["from external_inputs.monthly_usd"],
    )


def measure_c_drift(root: Path) -> Measurement:
    """Proxy: Shannon entropy of file-extension distribution over windowed history.

    Higher entropy AND change in entropy over time correlates with
    architectural drift (heterogeneous additions without consolidation).
    """
    exts: list[str] = []
    for f in _walk_files(root):
        ext = f.suffix.lower() or "<no-ext>"
        exts.append(ext)
    if not exts:
        return Measurement(axis="c_drift", value=0.0, confidence="low", notes=["empty repo"])

    ctr = Counter(exts)
    total = sum(ctr.values())
    h = -sum((c / total) * math.log2(c / total) for c in ctr.values())
    max_h = math.log2(len(ctr)) if len(ctr) > 1 else 1.0
    normalized = h / max_h if max_h > 0 else 0.0
    return Measurement(
        axis="c_drift",
        value=round(normalized, 3),
        confidence="low",
        notes=[
            "static-snapshot proxy; true drift needs windowed delta",
            f"distinct_exts={len(ctr)}",
            f"entropy_raw={h:.3f}",
        ],
    )


_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def relative_links(root: Path) -> list[tuple[Path, str, bool | None]]:
    """Every relative markdown link under `root`: (source file, target text, points to a file).

    The third item is True when the target exists, False when it points nowhere inside the
    repository, and None when the link could not be judged (empty path, outside the repository,
    or a path the file system refused). The c_loss reading counts the False ones.
    """
    found: list[tuple[Path, str, bool | None]] = []
    root_resolved = root.resolve()
    for f in _walk_files(root):
        if f.suffix.lower() != ".md":
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for _, target in _LINK_PATTERN.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#", "<")):
                continue
            # Strip anchor + query
            target_path = target.split("#", 1)[0].split("?", 1)[0]
            if not target_path:
                found.append((f, target, None))
                continue
            try:
                resolved = (f.parent / target_path).resolve()
            except OSError:
                # Pathological link target (e.g. embedded data: URI). Skip.
                found.append((f, target, None))
                continue
            try:
                resolved.relative_to(root_resolved)
            except ValueError:
                # Points outside repo. Don't count as orphan.
                found.append((f, target, None))
                continue
            try:
                exists = resolved.exists()
            except OSError:
                # File-name-too-long, etc. Treat as not-an-orphan (skip).
                found.append((f, target, None))
                continue
            found.append((f, target, exists))
    return found


def measure_c_loss(root: Path) -> Measurement:
    """Proxy: orphan markdown links inside .md files.

    Counts relative links inside .md files that point to non-existent paths
    within the same repo. Cheap and surprisingly informative for memory and
    docs-heavy K classes.
    """
    links = relative_links(root)
    total = len(links)
    orphans = sum(1 for _, _, exists in links if exists is False)

    rate = (orphans / total) if total else 0.0
    return Measurement(
        axis="c_loss",
        value=round(rate, 4),
        confidence="medium" if total > 0 else "low",
        notes=[
            f"orphan_links={orphans}",
            f"total_relative_links={total}",
        ],
    )


def measure_c_derive(root: Path) -> Measurement:
    """Proxy: ratio of TRACKED files in conventionally-derived folders.

    Conventionally-derived: dist/, build/, generated/, derived/, .next/,
    __pycache__. We restrict to git-tracked files to avoid environmental
    non-determinism (e.g. pytest creating __pycache__/ inside a cloned
    repo after the first measurement). This makes c_derive bit-identical
    across runs against the same SHA.

    If git is unavailable, falls back to filesystem walk with confidence=low.
    """
    derived_dirs = {"dist", "build", "generated", "derived", ".next", "__pycache__"}
    out = _git(["ls-files", "-z"], root)
    if out is None:
        # No git: best-effort filesystem walk + low confidence.
        total = 0
        derived = 0
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if any(part == ".git" for part in path.parts):
                continue
            total += 1
            if any(part in derived_dirs for part in path.parts):
                derived += 1
        if total == 0:
            return Measurement(axis="c_derive", value=0.0, confidence="low", notes=["empty repo, no git"])
        return Measurement(
            axis="c_derive",
            value=round(derived / total, 4),
            confidence="low",
            notes=[
                "INVENT-tier proxy; git unavailable so used fs walk (non-deterministic)",
                f"derived_files={derived}",
                f"total_files={total}",
            ],
        )
    files = [f for f in out.split("\0") if f]
    total = len(files)
    derived = sum(1 for f in files if any(part in derived_dirs for part in f.split("/")))
    if total == 0:
        return Measurement(axis="c_derive", value=0.0, confidence="low", notes=["empty git index"])
    ratio = derived / total
    return Measurement(
        axis="c_derive",
        value=round(ratio, 4),
        confidence="low",
        notes=[
            "INVENT-tier proxy; real c_derive requires lineage graph",
            f"derived_files={derived}",
            f"total_files={total}",
        ],
    )


# ---- Composite measurement --------------------------------------------------


def measure_repo(
    root: Path,
    external_inputs: dict | None = None,
    measured_at: str | None = None,
) -> CoreVector:
    """Produce a full C_core vector for `root`.

    `external_inputs`:
      - monthly_usd: float — for c_money
    `measured_at`:
      - ISO-8601 UTC timestamp. Used by c_modify to freeze the 365d window
        against a logical clock. Bench callers MUST pass this.
    """
    root = root.resolve()
    external_inputs = external_inputs or {}
    measurements = {
        "c_find": measure_c_find(root),
        "c_modify": measure_c_modify(root, until=measured_at),
        "c_storage": measure_c_storage(root),
        "c_money": measure_c_money(root, external_inputs.get("monthly_usd")),
        "c_drift": measure_c_drift(root),
        "c_loss": measure_c_loss(root),
        "c_derive": measure_c_derive(root),
    }
    return CoreVector(repo=root, measurements=measurements)


def _main() -> int:
    import argparse
    import json

    parser = argparse.ArgumentParser(description="A* passive C_core measurement.")
    parser.add_argument("root", type=Path)
    parser.add_argument("--monthly-usd", type=float, default=None)
    parser.add_argument("--json", action="store_true", help="emit JSON only")
    args = parser.parse_args()

    cv = measure_repo(args.root, {"monthly_usd": args.monthly_usd})
    out = {
        "repo": str(cv.repo),
        "axes": cv.as_dict(),
        "axis_specs": {
            a: {
                "unit": s.unit,
                "range": s.range,
                "normalization": s.normalization,
                "source": s.source,
                "default_confidence": s.default_confidence,
                "owner": s.owner,
                "update_cadence": s.update_cadence,
            }
            for a, s in AXIS_SPECS.items()
        },
    }
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(f"C_core for {cv.repo}")
        for axis, m in cv.measurements.items():
            print(f"  {axis}: {m.value} [{m.confidence}]  {'; '.join(m.notes)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
