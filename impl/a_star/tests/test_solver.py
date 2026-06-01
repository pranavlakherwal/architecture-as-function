"""Solver smoke tests on synthetic fixtures."""

from pathlib import Path

import pytest

from a_star.solver import build_model, emit_plan, introspect_repo, solve


def _seed_outbound_repo(root: Path) -> None:
    """Build a minimal outbound-pipeline-shaped fixture with known violations."""
    (root / "leads").mkdir()
    (root / "leads" / "c8.csv").write_text("email,name\n")
    (root / "leads" / "c9.csv").write_text("email,name\n")
    (root / "leads" / "c10.csv").write_text("email,name\n")

    (root / "suppression").mkdir()
    (root / "suppression" / "list.csv").write_text("email\n")
    (root / "suppression" / "manual_dnc.csv").write_text("email\n")
    (root / "suppression" / "history.json").write_text("[]")

    (root / "sequences").mkdir()
    (root / "sequences" / "build_c9.py").write_text("# builder\n")
    (root / "sequences" / "build_c10.py").write_text("# builder\n")
    (root / "sequences" / "models.py").write_text("# models\n")
    (root / "sequences" / "smartlead_client.py").write_text("# client\n")

    # Secret at rest
    (root / "secrets").mkdir()
    (root / "secrets" / ".env").write_text("SMARTLEAD_KEY=xxx\n")

    # Derived/cache
    (root / "output").mkdir()
    (root / "output" / "report1.json").write_text("{}")
    (root / "output" / "report2.json").write_text("{}")
    (root / "output" / "report3.json").write_text("{}")


def test_introspect_finds_pii_and_secret(tmp_path: Path):
    _seed_outbound_repo(tmp_path)
    facts = introspect_repo(tmp_path)
    by_name = {f.rel_path: f for f in facts}
    assert by_name["leads"].has_pii_signal
    assert by_name["secrets"].has_secret_at_rest
    assert by_name["output"].looks_derived
    assert "suppression_list" in by_name["suppression"].scopes_matched
    assert "sequence_state" in by_name["sequences"].scopes_matched
    assert "lead_records" in by_name["leads"].scopes_matched


def test_solver_returns_sat_on_clean_fixture(tmp_path: Path):
    _seed_outbound_repo(tmp_path)
    facts = introspect_repo(tmp_path)
    opt, state = build_model(facts, k_class="outbound-pipeline")
    result = solve(opt, state)
    assert result.status == "sat", result


def test_canonical_uniqueness_per_scope(tmp_path: Path):
    _seed_outbound_repo(tmp_path)
    facts = introspect_repo(tmp_path)
    opt, state = build_model(facts)
    result = solve(opt, state)
    assert result.status == "sat"
    # IC1: exactly one canonical per scope that has candidates.
    by_scope: dict[str, int] = {}
    for d in result.decisions:
        for scope in d.canonical_for:
            by_scope[scope] = by_scope.get(scope, 0) + 1
    # suppression_list, sequence_state, lead_records each should have exactly one.
    for scope in ("suppression_list", "sequence_state", "lead_records"):
        assert by_scope.get(scope, 0) == 1, f"scope {scope}: count={by_scope.get(scope, 0)}"


def test_secret_folder_scheduled_for_destruction(tmp_path: Path):
    _seed_outbound_repo(tmp_path)
    facts = introspect_repo(tmp_path)
    opt, state = build_model(facts)
    result = solve(opt, state)
    secrets_decision = next(d for d in result.decisions if d.rel_path == "secrets")
    assert secrets_decision.retention in ("scheduled_for_destruction", "destroyed")


def test_pii_folder_must_have_manifest(tmp_path: Path):
    _seed_outbound_repo(tmp_path)
    facts = introspect_repo(tmp_path)
    opt, state = build_model(facts)
    result = solve(opt, state)
    leads_decision = next(d for d in result.decisions if d.rel_path == "leads")
    assert leads_decision.manifest_present


def test_emit_plan_produces_primitives(tmp_path: Path):
    _seed_outbound_repo(tmp_path)
    facts = introspect_repo(tmp_path)
    opt, state = build_model(facts)
    result = solve(opt, state)
    plan = emit_plan(result, facts, k_class="outbound-pipeline")
    assert plan.primitives, "expected at least one primitive on dirty fixture"
    op_set = {p.op for p in plan.primitives}
    # Manifest creation and source-of-truth assignment should both appear.
    assert "UPDATE_MANIFEST" in op_set
    assert "SET_SOURCE_OF_TRUTH" in op_set
    assert "SCHEDULE_DESTRUCTION" in op_set


def test_plan_is_topologically_ordered(tmp_path: Path):
    _seed_outbound_repo(tmp_path)
    facts = introspect_repo(tmp_path)
    opt, state = build_model(facts)
    result = solve(opt, state)
    plan = emit_plan(result, facts, k_class="outbound-pipeline")
    # UPDATE_MANIFEST should never appear after SCHEDULE_DESTRUCTION.
    last_seen_destruction_idx = None
    for i, p in enumerate(plan.primitives):
        if p.op == "SCHEDULE_DESTRUCTION":
            last_seen_destruction_idx = i
        if p.op == "UPDATE_MANIFEST" and last_seen_destruction_idx is not None:
            pytest.fail("UPDATE_MANIFEST appeared after SCHEDULE_DESTRUCTION")


def test_existing_manifest_is_preserved(tmp_path: Path):
    _seed_outbound_repo(tmp_path)
    # Drop a real manifest into `leads` so the solver should not need a new one.
    import json

    manifest = {
        "scope": "Outbound lead records for active campaigns.",
        "exclusions": [],
        "allowed_artifact_types": ["lead_csv"],
        "owner": "pranav",
        "lifecycle_status": "production",
        "required_metadata": ["source_cohort"],
        "outbound_relations": [],
        "review_cadence": "weekly",
        "retention": {"class": "active", "policy": "soft"},
    }
    (tmp_path / "leads" / ".manifest.json").write_text(json.dumps(manifest))
    facts = introspect_repo(tmp_path)
    opt, state = build_model(facts)
    result = solve(opt, state)
    plan = emit_plan(result, facts, k_class="outbound-pipeline")
    # No UPDATE_MANIFEST targeting `leads` should appear.
    leads_manifest_ops = [
        p for p in plan.primitives if p.op == "UPDATE_MANIFEST" and p.target == "leads"
    ]
    assert leads_manifest_ops == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
