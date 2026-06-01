"""CLI entry: A* run over a repo. Emits primitive plan as YAML.

Usage:
    python -m a_star.solver.cli /path/to/repo \
        --k outbound-pipeline \
        --out plan.yaml
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import build_model, emit_plan, introspect_repo, solve


def main() -> int:
    parser = argparse.ArgumentParser(description="A* v0.1 solver runner.")
    parser.add_argument("repo", type=Path)
    parser.add_argument("--k", default="outbound-pipeline", help="K class")
    parser.add_argument("--out", type=Path, default=None, help="Write plan to file (YAML if .yaml, JSON otherwise)")
    parser.add_argument("--timeout-ms", type=int, default=30_000)
    parser.add_argument(
        "--min-stable-files",
        type=int,
        default=3,
        help="Min file count for a folder to be a stable boundary",
    )
    args = parser.parse_args()

    facts = introspect_repo(args.repo, min_files_for_stable_boundary=args.min_stable_files)
    print(f"Introspected {len(facts)} folders under {args.repo}", file=sys.stderr)

    opt, state = build_model(facts, k_class=args.k)
    result = solve(opt, state, timeout_ms=args.timeout_ms)
    print(f"Solver status: {result.status}", file=sys.stderr)

    plan = emit_plan(result, facts, k_class=args.k)
    data = plan.to_dict()

    if args.out is None:
        print(json.dumps(data, indent=2, default=str))
    else:
        text = _serialize(data, args.out)
        args.out.write_text(text, encoding="utf-8")
        print(f"Wrote plan ({len(plan.primitives)} primitives) -> {args.out}", file=sys.stderr)
    return 0 if result.status == "sat" else 1


def _serialize(data: dict, out: Path) -> str:
    if out.suffix in (".yaml", ".yml"):
        try:
            import yaml

            return yaml.safe_dump(data, sort_keys=False, default_flow_style=False)
        except ImportError:
            pass
    return json.dumps(data, indent=2, default=str)


if __name__ == "__main__":
    raise SystemExit(main())
