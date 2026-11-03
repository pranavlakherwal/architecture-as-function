"""Manifest schema + validator tests."""

import json
from pathlib import Path

import pytest
from a_star.manifest import scan_repo, validate_manifest

MINIMAL_OK = {
    "scope": "Test folder for unit tests.",
    "exclusions": [],
    "allowed_artifact_types": ["test_fixture"],
    "owner": "pranav",
    "lifecycle_status": "bootstrap",
    "required_metadata": ["author"],
    "outbound_relations": [],
    "review_cadence": "monthly",
    "retention": {"class": "active", "policy": "none"},
}


def _write_manifest(folder: Path, data: dict, name: str = ".manifest.json") -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / name
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_minimal_valid_manifest(tmp_path: Path):
    _write_manifest(tmp_path, MINIMAL_OK)
    result = validate_manifest(tmp_path)
    assert result.ok, [str(v) for v in result.violations]
    assert result.manifest is not None
    assert result.manifest["scope"] == MINIMAL_OK["scope"]


def test_missing_required_field_flagged(tmp_path: Path):
    bad = dict(MINIMAL_OK)
    del bad["owner"]
    _write_manifest(tmp_path, bad)
    result = validate_manifest(tmp_path)
    assert not result.ok
    assert any("owner" in v.message for v in result.violations)


def test_invalid_lifecycle_status(tmp_path: Path):
    bad = dict(MINIMAL_OK)
    bad["lifecycle_status"] = "shipped"  # not in enum
    _write_manifest(tmp_path, bad)
    result = validate_manifest(tmp_path)
    assert not result.ok


def test_scheduled_destruction_requires_deadline(tmp_path: Path):
    bad = dict(MINIMAL_OK)
    bad["retention"] = {"class": "scheduled_for_destruction", "policy": "hard"}
    _write_manifest(tmp_path, bad)
    result = validate_manifest(tmp_path)
    assert not result.ok
    assert any("destruction_deadline" in v.message for v in result.violations)


def test_scheduled_destruction_with_deadline_ok(tmp_path: Path):
    good = dict(MINIMAL_OK)
    good["retention"] = {
        "class": "scheduled_for_destruction",
        "policy": "hard",
        "destruction_deadline": "2026-12-31",
    }
    _write_manifest(tmp_path, good)
    result = validate_manifest(tmp_path)
    assert result.ok, [str(v) for v in result.violations]


def test_outbound_relation_requires_target_and_type(tmp_path: Path):
    bad = dict(MINIMAL_OK)
    bad["outbound_relations"] = [{"target": "../other"}]  # missing type
    _write_manifest(tmp_path, bad)
    result = validate_manifest(tmp_path)
    assert not result.ok


def test_unknown_top_level_field_rejected(tmp_path: Path):
    bad = dict(MINIMAL_OK)
    bad["random_extra"] = True
    _write_manifest(tmp_path, bad)
    result = validate_manifest(tmp_path)
    assert not result.ok


def test_scan_repo_finds_nested_manifests(tmp_path: Path):
    _write_manifest(tmp_path / "a", MINIMAL_OK)
    _write_manifest(tmp_path / "b" / "c", MINIMAL_OK)
    results = scan_repo(tmp_path)
    folders_with_manifest = {r.folder for r in results if r.manifest_path}
    assert tmp_path / "a" in folders_with_manifest
    assert tmp_path / "b" / "c" in folders_with_manifest


def test_scan_repo_require_depth_flags_missing(tmp_path: Path):
    (tmp_path / "x").mkdir()
    (tmp_path / "y").mkdir()
    _write_manifest(tmp_path / "y", MINIMAL_OK)
    results = scan_repo(tmp_path, require_manifest_at_depth=1)
    violators = {r.folder for r in results if any(v.code == "MISSING_MANIFEST" for v in r.violations)}
    assert tmp_path / "x" in violators
    assert tmp_path / "y" not in violators


def test_scan_repo_skips_node_modules(tmp_path: Path):
    _write_manifest(tmp_path / "node_modules" / "pkg", MINIMAL_OK)
    results = scan_repo(tmp_path)
    assert all("node_modules" not in r.folder.parts for r in results)


def test_unparseable_manifest_flagged(tmp_path: Path):
    p = tmp_path / ".manifest.json"
    p.write_text("{this is not json", encoding="utf-8")
    result = validate_manifest(tmp_path)
    assert not result.ok
    assert result.violations[0].code == "MANIFEST_PARSE_ERROR"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
