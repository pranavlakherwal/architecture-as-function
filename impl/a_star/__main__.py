"""Command line entry for the A* reference implementation.

    python -m a_star measure PATH [--json] [--monthly-usd N] [--as-of YYYY-MM-DD]

From the repository root: PYTHONPATH=impl python3 -m a_star measure PATH
From the impl/ folder:    python3 -m a_star measure PATH

`measure` reads seven numbers from a repository without changing it, says where each
sits among the repositories we have measured, and names the three fixes to make first.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m a_star",
        description="A*: architecture as a function. Reference implementation commands.",
    )
    sub = parser.add_subparsers(dest="command")
    sub.required = True
    measure = sub.add_parser(
        "measure",
        help="read seven numbers from a repository and name the three fixes to make first",
        description="Read seven numbers from a repository and name the three fixes to make first.",
    )
    measure.add_argument("path", type=Path, help="the repository folder to measure")
    measure.add_argument("--json", action="store_true", help="print the same content as JSON")
    measure.add_argument(
        "--monthly-usd",
        type=float,
        default=None,
        help="what the system costs to run each month, if you know it",
    )
    measure.add_argument(
        "--as-of",
        metavar="YYYY-MM-DD",
        default=None,
        help="read the repository as of this date; the 365 day change window ends there",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "measure":
        from a_star.measurement.report import run_measure

        return run_measure(
            args.path,
            as_json=args.json,
            monthly_usd=args.monthly_usd,
            as_of=args.as_of,
            out=sys.stdout,
            err=sys.stderr,
        )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
