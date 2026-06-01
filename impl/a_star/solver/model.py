"""Z3 Optimize model for A*.

Per A_STAR_v0.md §7: hard integrity constraints via assert, soft objectives
via assert-soft with weights from W_K, lexicographic multi-objective mode.

Decision variables per folder F (introspected fact):
  retention_class[F]   in {active, archived, scheduled_for_destruction, destroyed}
  manifest_present[F]  : Bool      (must be true for stable boundaries; IC3)
  is_canonical[F, scope] : Bool    (exactly one per matched scope; IC1)

Constraints encoded:
  - IC1: per scope, sum(is_canonical[F, scope]) == 1
  - IC2: secret-at-rest -> retention class != active (must rotate)
         PII signal in non-archive folder -> manifest_present == True
  - IC3: stable_boundary -> manifest_present == True
  - H_K outbound-pipeline:
      * suppression_list scope must have a canonical assignment
      * sequence_state scope must have a canonical assignment
      * archived folders cannot also be canonical sources

Soft objectives (W_K outbound-pipeline = c_money>c_drift>c_modify):
  - minimize count(active retention on folders with no fresh activity proxy)
    (c_money proxy: stale-active data costs storage and risk)
  - minimize count(stable_boundary AND not manifest_present)
    (c_drift + c_modify proxy: undocumented contracts decay)
  - minimize count(scopes with zero canonical candidate)
    (c_loss proxy: silent orphaning)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import z3

from ..profiles import KProfile, get_profile
from .introspect import SCOPES, FolderFact

RetentionClass = Literal[
    "active", "archived", "scheduled_for_destruction", "destroyed"
]
RETENTION_VALUES: tuple[RetentionClass, ...] = (
    "active",
    "archived",
    "scheduled_for_destruction",
    "destroyed",
)


@dataclass
class FolderDecision:
    rel_path: str
    retention: RetentionClass
    manifest_present: bool
    canonical_for: list[str] = field(default_factory=list)


@dataclass
class SolveResult:
    status: str  # "sat" | "unsat" | "unknown"
    decisions: list[FolderDecision] = field(default_factory=list)
    unsat_core: list[str] = field(default_factory=list)
    objective_values: dict[str, int] = field(default_factory=dict)


def build_model(
    facts: list[FolderFact],
    k_class: str = "outbound-pipeline",
) -> tuple[z3.Optimize, dict]:
    """Build the Z3 Optimize problem from folder facts.

    Returns the solver and a dict of named variables so the caller can
    extract decisions after solving.
    """
    profile: KProfile = get_profile(k_class)  # type: ignore[arg-type]
    opt = z3.Optimize()

    # ---- Decision variables ------------------------------------------------
    retention: dict[str, z3.ArithRef] = {}
    manifest_present: dict[str, z3.BoolRef] = {}
    canonical: dict[tuple[str, str], z3.BoolRef] = {}  # (folder, scope) -> Bool

    for f in facts:
        # Encode retention as a 0..3 integer; we map to RETENTION_VALUES.
        r = z3.Int(f"retention__{_sanitize(f.rel_path)}")
        opt.add(r >= 0, r <= 3)
        retention[f.rel_path] = r

        mp = z3.Bool(f"manifest__{_sanitize(f.rel_path)}")
        manifest_present[f.rel_path] = mp
        # Initial-value pin: if it actually has a manifest, must stay true.
        if f.has_manifest:
            opt.add(mp == True)  # noqa: E712

        for scope in f.scopes_matched:
            key = (f.rel_path, scope)
            canonical[key] = z3.Bool(f"canonical__{_sanitize(f.rel_path)}__{scope}")

    # ---- IC1: per scope, exactly one canonical -----------------------------
    for scope in SCOPES:
        candidates = [v for (_, s), v in canonical.items() if s == scope]
        if not candidates:
            # No folder matched this scope. We can't force IC1 here; we
            # surface this as a soft penalty below.
            continue
        opt.add(z3.PbEq([(v, 1) for v in candidates], 1))

    # ---- IC2 + IC3 ---------------------------------------------------------
    for f in facts:
        r = retention[f.rel_path]
        mp = manifest_present[f.rel_path]

        # IC2: secret at rest -> retention != active. Must be scheduled or
        # destroyed (rotate-or-purge). Encode: retention >= 2.
        if f.has_secret_at_rest:
            opt.add(r >= _retention_index("scheduled_for_destruction"))

        # IC2: PII in non-archive folder -> must have manifest with declared
        # retention. We encode the manifest requirement; retention class is
        # free but defaults are pushed by soft objectives.
        if f.has_pii_signal and not f.looks_archived:
            opt.add(mp == True)  # noqa: E712

        # IC3: stable boundary -> manifest present.
        if f.is_stable_boundary:
            opt.add(mp == True)  # noqa: E712

        # H_K rider: archived folders cannot be canonical.
        if f.looks_archived:
            for scope in f.scopes_matched:
                opt.add(canonical[(f.rel_path, scope)] == False)  # noqa: E712

    # ---- H_K outbound-pipeline anchor constraints --------------------------
    # If suppression_list / sequence_state scopes exist at all in the repo,
    # IC1 already forces canonicality. If they don't exist, we flag as a
    # soft cost (a missing scope is a discovery problem, not a sat problem).

    # ---- Soft objectives (weighted) ----------------------------------------
    w = profile.soft_weights
    # Convert weights to integers for Z3 weighted soft constraints. Use a
    # consistent scale; lex modes order by the order in which we add.
    scale = 100
    obj_names: dict[str, int] = {}

    # c_money proxy: number of folders whose retention is "active" but the
    # folder looks derived/archived (stale active is a cost).
    for f in facts:
        r = retention[f.rel_path]
        if f.looks_derived or f.looks_archived:
            opt.add_soft(
                r != _retention_index("active"),
                weight=int(w["c_money"] * scale),
                id="c_money",
            )

    # c_drift + c_modify proxy: stable boundary without manifest. (Soft only
    # because we already hard-asserted is_stable_boundary -> mp; this softly
    # discourages folders just below the threshold too.)
    for f in facts:
        if not f.is_stable_boundary and f.file_count >= 1:
            opt.add_soft(
                manifest_present[f.rel_path] == True,  # noqa: E712
                weight=int((w["c_drift"] + w["c_modify"]) * scale / 2),
                id="c_drift_modify",
            )

    # c_loss proxy: per scope, penalize having zero matched folders.
    for scope in SCOPES:
        candidates = [v for (_, s), v in canonical.items() if s == scope]
        if not candidates:
            # Add a constant soft constraint that is always violated; that
            # encodes "missing scope is a cost we'd like to know about".
            dummy = z3.Bool(f"scope_present__{scope}")
            opt.add(dummy == False)  # noqa: E712
            opt.add_soft(
                dummy,
                weight=int(w["c_loss"] * scale),
                id="c_loss",
            )

    # c_storage proxy: prefer ARCHIVE over keeping derived big folders active.
    # (Already covered partly by c_money; add a lighter touch by storage class.)
    # Skipped at v0.1: would need normalized byte costs.

    obj_names["c_money"] = int(w["c_money"] * scale)
    obj_names["c_drift_modify"] = int((w["c_drift"] + w["c_modify"]) * scale / 2)
    obj_names["c_loss"] = int(w["c_loss"] * scale)

    state = {
        "retention": retention,
        "manifest_present": manifest_present,
        "canonical": canonical,
        "facts_by_path": {f.rel_path: f for f in facts},
        "k_class": k_class,
        "obj_weights": obj_names,
    }
    return opt, state


def solve(opt: z3.Optimize, state: dict, timeout_ms: int = 30_000) -> SolveResult:
    opt.set("timeout", timeout_ms)
    check = opt.check()
    status = str(check)

    if check != z3.sat:
        # Z3 Optimize does not expose unsat core directly; we surface the
        # check status. For v0.1 we record the status; v0.2 will switch to
        # incremental push/pop to localize the failing constraint set.
        return SolveResult(status=status)

    model = opt.model()
    retention = state["retention"]
    manifest_present = state["manifest_present"]
    canonical = state["canonical"]
    facts_by_path = state["facts_by_path"]

    decisions: list[FolderDecision] = []
    for rel_path, r_var in retention.items():
        r_val = model.eval(r_var, model_completion=True).as_long()
        retention_class = RETENTION_VALUES[r_val]
        mp_val = bool(model.eval(manifest_present[rel_path], model_completion=True))
        scopes = [
            scope
            for (p, scope), v in canonical.items()
            if p == rel_path and bool(model.eval(v, model_completion=True))
        ]
        decisions.append(
            FolderDecision(
                rel_path=rel_path,
                retention=retention_class,
                manifest_present=mp_val,
                canonical_for=scopes,
            )
        )

    # Tally objective stats for diagnostic output.
    obj: dict[str, int] = {}
    obj["folders_total"] = len(decisions)
    obj["manifests_required"] = sum(1 for d in decisions if d.manifest_present)
    obj["scheduled_destruction"] = sum(
        1 for d in decisions if d.retention == "scheduled_for_destruction"
    )
    obj["archived"] = sum(1 for d in decisions if d.retention == "archived")
    obj["canonical_assignments"] = sum(len(d.canonical_for) for d in decisions)

    return SolveResult(status=status, decisions=decisions, objective_values=obj)


def _retention_index(name: RetentionClass) -> int:
    return RETENTION_VALUES.index(name)


def _sanitize(rel_path: str) -> str:
    return rel_path.replace("/", "__").replace("-", "_").replace(".", "_") or "root"
