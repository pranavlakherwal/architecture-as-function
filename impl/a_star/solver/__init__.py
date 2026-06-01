"""A* Z3 Optimize solver.

Wires:
  - introspect.py: scan a repo, extract folder-level facts
  - model.py: build Z3 Optimize problem from facts + K profile
  - plan.py: convert Z3 solution -> primitive transaction (YAML)
"""

from .introspect import FolderFact, introspect_repo
from .model import (
    SolveResult,
    build_model,
    solve,
)
from .plan import emit_plan

__all__ = [
    "FolderFact",
    "introspect_repo",
    "SolveResult",
    "build_model",
    "solve",
    "emit_plan",
]
