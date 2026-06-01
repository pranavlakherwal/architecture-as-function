"""Convert a Z3 SolveResult into a primitive transaction plan.

Emits the 9-op primitive set from A_STAR_v0.md §9 as a YAML DAG with
inverse plan stubs. Only operations that change the current state vs
introspected facts are emitted.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .introspect import FolderFact
from .model import FolderDecision, SolveResult

PRIMITIVE_OPS: tuple[str, ...] = (
    "CREATE_FOLDER",
    "ARCHIVE_FOLDER",
    "MOVE_ARTIFACT",
    "DUPLICATE_TO_CACHE",
    "SET_SOURCE_OF_TRUTH",
    "UPDATE_MANIFEST",
    "UPSERT_RELATION",
    "MIGRATE_PERSISTENCE",
    "SCHEDULE_DESTRUCTION",
)


@dataclass
class Primitive:
    op: str
    target: str
    inputs: dict[str, Any] = field(default_factory=dict)
    inverse: dict[str, Any] | None = None
    rationale: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "op": self.op,
            "target": self.target,
            "inputs": self.inputs,
            "rationale": self.rationale,
        }
        if self.inverse is not None:
            d["inverse"] = self.inverse
        return d


@dataclass
class PrimitivePlan:
    k_class: str
    primitives: list[Primitive]
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "k_class": self.k_class,
            "primitives": [p.to_dict() for p in self.primitives],
            "diagnostics": self.diagnostics,
        }


def emit_plan(
    result: SolveResult,
    facts: list[FolderFact],
    k_class: str,
) -> PrimitivePlan:
    """Diff decisions vs current facts; emit only the primitives that change state."""
    if result.status != "sat":
        return PrimitivePlan(
            k_class=k_class,
            primitives=[],
            diagnostics={"solver_status": result.status},
        )

    by_path: dict[str, FolderFact] = {f.rel_path: f for f in facts}
    primitives: list[Primitive] = []

    for d in result.decisions:
        f = by_path.get(d.rel_path)
        if f is None:
            continue

        # UPDATE_MANIFEST when manifest is required but missing.
        if d.manifest_present and not f.has_manifest:
            primitives.append(
                Primitive(
                    op="UPDATE_MANIFEST",
                    target=d.rel_path or "<root>",
                    inputs={
                        "create_with_template": True,
                        "required_fields": [
                            "scope",
                            "exclusions",
                            "allowed_artifact_types",
                            "owner",
                            "lifecycle_status",
                            "required_metadata",
                            "outbound_relations",
                            "review_cadence",
                            "retention",
                        ],
                    },
                    inverse={"op": "DELETE_MANIFEST", "target": d.rel_path or "<root>"},
                    rationale=_manifest_rationale(f),
                )
            )

        # SET_SOURCE_OF_TRUTH per scope assigned canonical.
        for scope in d.canonical_for:
            primitives.append(
                Primitive(
                    op="SET_SOURCE_OF_TRUTH",
                    target=d.rel_path or "<root>",
                    inputs={"scope": scope},
                    inverse={
                        "op": "SET_SOURCE_OF_TRUTH",
                        "target": "<previous_owner>",
                        "inputs": {"scope": scope},
                    },
                    rationale=f"IC1: canonical assignment for scope `{scope}`.",
                )
            )

        # SCHEDULE_DESTRUCTION when retention class moves to scheduled_for_destruction.
        if d.retention == "scheduled_for_destruction":
            primitives.append(
                Primitive(
                    op="SCHEDULE_DESTRUCTION",
                    target=d.rel_path or "<root>",
                    inputs={
                        "policy": "sanitize" if f.has_secret_at_rest else "hard",
                        "deadline_relative": "+30d",
                        "approval_required": True,
                    },
                    inverse={
                        "op": "CANCEL_DESTRUCTION",
                        "target": d.rel_path or "<root>",
                    },
                    rationale=(
                        "IC2: secret-at-rest must rotate or purge."
                        if f.has_secret_at_rest
                        else "IC2: declared destruction per retention schedule."
                    ),
                )
            )

        # ARCHIVE_FOLDER when retention class moves to archived.
        if d.retention == "archived" and not f.looks_archived:
            primitives.append(
                Primitive(
                    op="ARCHIVE_FOLDER",
                    target=d.rel_path or "<root>",
                    inputs={"retention_window": "see_manifest"},
                    inverse={"op": "RESTORE_FOLDER", "target": d.rel_path or "<root>"},
                    rationale="Moved to archive namespace per K-class policy.",
                )
            )

    diagnostics = {
        "solver_status": result.status,
        "objective_values": result.objective_values,
        "primitive_count": len(primitives),
        "primitive_op_distribution": _op_histogram(primitives),
    }
    return PrimitivePlan(
        k_class=k_class,
        primitives=_topological_sort(primitives),
        diagnostics=diagnostics,
    )


def _manifest_rationale(f: FolderFact) -> str:
    if f.is_stable_boundary:
        return "IC3: stable boundary requires manifest."
    if f.has_pii_signal:
        return "IC2: PII signal requires declared retention via manifest."
    return "Soft objective: manifest reduces c_drift and c_modify."


def _op_histogram(primitives: list[Primitive]) -> dict[str, int]:
    h: dict[str, int] = {}
    for p in primitives:
        h[p.op] = h.get(p.op, 0) + 1
    return h


def _topological_sort(primitives: list[Primitive]) -> list[Primitive]:
    """Order primitives so that dependencies precede dependents.

    v0.1 ordering rule (deterministic, K-agnostic):
      1. UPDATE_MANIFEST first (declares scope before other ops touch folders)
      2. SET_SOURCE_OF_TRUTH (canonicality binds after scope exists)
      3. ARCHIVE_FOLDER
      4. SCHEDULE_DESTRUCTION (last; touches policy clocks)
    """
    order = {
        "UPDATE_MANIFEST": 0,
        "SET_SOURCE_OF_TRUTH": 1,
        "UPSERT_RELATION": 2,
        "MOVE_ARTIFACT": 3,
        "DUPLICATE_TO_CACHE": 4,
        "CREATE_FOLDER": 5,
        "MIGRATE_PERSISTENCE": 6,
        "ARCHIVE_FOLDER": 7,
        "SCHEDULE_DESTRUCTION": 8,
    }
    return sorted(primitives, key=lambda p: (order.get(p.op, 99), p.target))
