"""Build the fleet reference: the sorted values of each reading across many repositories.

This script reads private machines and ships only numbers. It walks the folder you name,
finds every git repository one or two levels down, measures each with `measure_repo`, and
writes `fleet_reference.json` holding three things: the date, the count of repositories,
and one sorted list of numbers per reading. No path, no repository name and no per
repository row is written. A reader of the JSON learns how many repositories were measured
and the spread of each reading, and nothing else.

Skipped on the walk: node_modules, .git internals, any folder named _archive or _archives,
and any folder whose name contains "backup" or "worktree". A repository that fails to
measure, or takes longer than the per repository budget (default 120 seconds), is skipped
and counted in the summary printed to stderr.

Run from the repository root:

    PYTHONPATH=impl python3 impl/a_star/measurement/build_fleet_reference.py --root FOLDER

Add --out to write somewhere other than impl/a_star/measurement/fleet_reference.json,
and --per-repo-seconds to change the budget.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import signal
import sys
from pathlib import Path

from a_star.measurement.core_vector import measure_repo
from a_star.measurement.report import FLEET_REFERENCE_PATH, READING_KEYS

SKIP_NAMES: frozenset[str] = frozenset({"node_modules", ".git", "_archive", "_archives"})
SKIP_FRAGMENTS: tuple[str, ...] = ("backup", "worktree")


def _skipped(name: str) -> bool:
    low = name.lower()
    if name in SKIP_NAMES:
        return True
    return any(fragment in low for fragment in SKIP_FRAGMENTS)


def _is_repo(folder: Path) -> bool:
    # A .git folder, or a .git file (a worktree or submodule pointer).
    return (folder / ".git").exists()


def discover_repos(root: Path, max_depth: int = 2) -> list[Path]:
    """Every git repository under `root` at depth 1 to `max_depth`, sorted.

    A repository found at depth 1 is not searched for repositories inside it.
    """
    found: list[Path] = []

    def walk(folder: Path, depth: int) -> None:
        try:
            children = sorted(p for p in folder.iterdir() if p.is_dir() and not p.is_symlink())
        except OSError:
            return
        for child in children:
            if _skipped(child.name):
                continue
            if _is_repo(child):
                found.append(child)
                continue
            if depth < max_depth:
                walk(child, depth + 1)

    walk(Path(root), 1)
    return found


def build_reference(vectors: list[dict[str, float]], as_of: str) -> dict:
    """Fold per repository value dicts into the published shape: as_of, n, and sorted lists."""
    out: dict = {"as_of": as_of, "n": len(vectors)}
    for key in READING_KEYS:
        # Adding 0.0 turns a negative zero from the entropy formula into a plain 0.0.
        out[key] = sorted(float(v[key]) + 0.0 for v in vectors)
    return out


class _OverBudget(Exception):
    """Raised inside a measurement that ran past its time budget."""


def _measure_within(repo: Path, seconds: float) -> dict[str, float]:
    """Measure one repository, raising _OverBudget if it runs past `seconds`.

    Uses SIGALRM where the platform has it (macOS, Linux). Elsewhere there is no budget.
    """
    if seconds <= 0 or not hasattr(signal, "SIGALRM"):
        return measure_repo(repo).values_only()

    def _alarm(signum, frame):
        raise _OverBudget()

    previous = signal.signal(signal.SIGALRM, _alarm)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        return measure_repo(repo).values_only()
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def measure_all(
    repos: list[Path], err=sys.stderr, per_repo_seconds: float = 120.0
) -> tuple[list[dict[str, float]], int]:
    """Measure each repository. Returns the value dicts and how many repositories were skipped.

    A repository is skipped when measuring it raises or runs past `per_repo_seconds`.
    """
    vectors: list[dict[str, float]] = []
    skipped = 0
    for i, repo in enumerate(repos, 1):
        try:
            vectors.append(_measure_within(repo, per_repo_seconds))
        except Exception:  # noqa: BLE001  a repository that cannot be read in time is skipped, not fatal
            skipped += 1
        print(f"measured {i} of {len(repos)}, skipped {skipped}", file=err, flush=True)
    return vectors, skipped


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the fleet reference from the repositories under a folder.")
    parser.add_argument("--root", type=Path, required=True, help="the folder whose repositories are measured")
    parser.add_argument("--out", type=Path, default=FLEET_REFERENCE_PATH, help="where to write the JSON")
    parser.add_argument("--max-depth", type=int, default=2, help="how many folder levels down to look (default 2)")
    parser.add_argument("--as-of", default=None, help="the date to record, YYYY-MM-DD (default today)")
    parser.add_argument(
        "--per-repo-seconds",
        type=float,
        default=120.0,
        help="skip a repository that takes longer than this to measure (default 120, 0 for no budget)",
    )
    args = parser.parse_args(argv)

    if not args.root.is_dir():
        print(f"build_fleet_reference: {args.root} is not a directory", file=sys.stderr)
        return 2
    repos = discover_repos(args.root, max_depth=args.max_depth)
    vectors, skipped = measure_all(repos, per_repo_seconds=args.per_repo_seconds)
    as_of = args.as_of or _dt.date.today().isoformat()
    reference = build_reference(vectors, as_of)
    args.out.write_text(json.dumps(reference, indent=1) + "\n", encoding="utf-8")
    print(
        f"wrote {args.out}: n={reference['n']} repositories, {skipped} skipped on error or budget, as_of={as_of}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
