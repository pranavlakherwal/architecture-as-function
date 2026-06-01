"""Tests for tools/stub_manifest.py.

Covers:
  - purpose inference (python + tests, mixed extensions, empty)
  - ignore patterns (.git, node_modules, archive)
  - parent-manifest inheritance (k_class, owner, review_cadence)
  - generated stub validates against the A* MANIFEST_SCHEMA
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Make `tools` and `a_star` importable when pytest is run from impl/.
_IMPL_ROOT = Path(__file__).resolve().parent.parent
if str(_IMPL_ROOT) not in sys.path:
    sys.path.insert(0, str(_IMPL_ROOT))

from tools import stub_manifest  # noqa: E402

yaml = pytest.importorskip("yaml")


# ---------------------------------------------------------------------------
# Purpose inference
# ---------------------------------------------------------------------------

def test_purpose_python_with_tests(tmp_path: Path):
    (tmp_path / "core.py").write_text("x = 1")
    (tmp_path / "helpers.py").write_text("y = 2")
    (tmp_path / "test_core.py").write_text("def test_x(): pass")
    files = list(tmp_path.iterdir())
    purpose = stub_manifest.infer_purpose(tmp_path, files, [])
    assert "python" in purpose
    assert "with tests" in purpose


def test_purpose_mixed_extensions(tmp_path: Path):
    (tmp_path / "schema.json").write_text("{}")
    (tmp_path / "config.yaml").write_text("a: 1")
    (tmp_path / "doc.md").write_text("# x")
    files = list(tmp_path.iterdir())
    purpose = stub_manifest.infer_purpose(tmp_path, files, [])
    # Top-2 extensions become labels.
    assert any(label in purpose for label in ("json", "yaml", "markdown"))


def test_purpose_empty_folder(tmp_path: Path):
    purpose = stub_manifest.infer_purpose(tmp_path, [], [])
    assert "empty" in purpose.lower()


# ---------------------------------------------------------------------------
# Ignore patterns
# ---------------------------------------------------------------------------

def test_ignore_patterns_skip_node_modules_and_git(tmp_path: Path):
    (tmp_path / ".git" / "objects").mkdir(parents=True)
    (tmp_path / ".git" / "objects" / "x.bin").write_text("x")
    (tmp_path / "node_modules" / "pkg").mkdir(parents=True)
    (tmp_path / "node_modules" / "pkg" / "index.js").write_text("//")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("a=1")

    report = stub_manifest.generate(tmp_path, apply=False)
    all_rels = {r.rel for r in report.results}
    wrote_rels = {r.rel for r in report.results if r.action == "would_write"}
    # src should be a write target; .git and node_modules subtrees should not
    # appear in the report at all (the walker prunes them before they're seen).
    assert "src" in wrote_rels
    assert not any(r.startswith(".git") for r in all_rels)
    assert not any(r.startswith("node_modules") for r in all_rels)
    # And no manifest was simulated inside them.
    assert not (tmp_path / ".git" / ".manifest.yaml").exists()
    assert not (tmp_path / "node_modules" / ".manifest.yaml").exists()


def test_ignore_pattern_archive(tmp_path: Path):
    (tmp_path / "archive").mkdir()
    (tmp_path / "archive" / "old.txt").write_text("legacy")
    report = stub_manifest.generate(tmp_path, apply=False)
    rels_written = {r.rel for r in report.results if r.action == "would_write"}
    assert "archive" not in rels_written


# ---------------------------------------------------------------------------
# Parent inheritance
# ---------------------------------------------------------------------------

def test_parent_inheritance_of_k_class_and_owner(tmp_path: Path):
    # Parent manifest at root.
    parent_doc = {
        "manifest_version": "1",
        "scope": "Test root with declared contract for inheritance tests.",
        "exclusions": [],
        "allowed_artifact_types": ["test_fixture"],
        "owner": "team-x",
        "lifecycle_status": "production",
        "required_metadata": [],
        "outbound_relations": [],
        "review_cadence": "monthly",
        "retention": {"class": "active", "policy": "none"},
        "k_class": "outbound-pipeline",
    }
    (tmp_path / ".manifest.yaml").write_text(yaml.safe_dump(parent_doc))

    # Child folder with no manifest.
    child = tmp_path / "child"
    child.mkdir()
    (child / "a.py").write_text("x=1")

    stub_manifest.generate(tmp_path, apply=True)

    written = yaml.safe_load((child / ".manifest.yaml").read_text())
    assert written["k_class"] == "outbound-pipeline"
    assert written["owner"] == "team-x"
    assert written["review_cadence"] == "monthly"
    # lifecycle is always reset to bootstrap on stubs (never inherited as production).
    assert written["lifecycle_status"] == "bootstrap"


def test_no_parent_falls_back_to_unclassified(tmp_path: Path):
    child = tmp_path / "lonely"
    child.mkdir()
    (child / "note.md").write_text("# n")
    stub_manifest.generate(tmp_path, apply=True)
    written = yaml.safe_load((child / ".manifest.yaml").read_text())
    assert written["k_class"] == "unclassified"
    assert "unknown" in written["owner"]


# ---------------------------------------------------------------------------
# Schema conformance
# ---------------------------------------------------------------------------

def test_generated_stub_passes_a_star_schema(tmp_path: Path):
    """A generated stub must validate against the real MANIFEST_SCHEMA."""
    pytest.importorskip("jsonschema")
    from jsonschema import Draft202012Validator

    sys.path.insert(0, str(_IMPL_ROOT))
    from a_star.manifest.schema import MANIFEST_SCHEMA

    sub = tmp_path / "src" / "feature"
    sub.mkdir(parents=True)
    (sub / "a.py").write_text("x=1")
    (sub / "test_a.py").write_text("def test_x(): pass")

    stub_manifest.generate(tmp_path, apply=True)

    written = yaml.safe_load((sub / ".manifest.yaml").read_text())
    errors = sorted(
        Draft202012Validator(MANIFEST_SCHEMA).iter_errors(written),
        key=lambda e: list(e.path),
    )
    assert not errors, [f"{list(e.path)}: {e.message}" for e in errors]


# ---------------------------------------------------------------------------
# Dry-run vs apply
# ---------------------------------------------------------------------------

def test_dry_run_does_not_write(tmp_path: Path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x=1")
    stub_manifest.generate(tmp_path, apply=False)
    assert not (tmp_path / "src" / ".manifest.yaml").exists()


def test_apply_writes(tmp_path: Path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x=1")
    stub_manifest.generate(tmp_path, apply=True)
    assert (tmp_path / "src" / ".manifest.yaml").exists()
    text = (tmp_path / "src" / ".manifest.yaml").read_text()
    assert "AUTO-GENERATED STUB MANIFEST" in text
    assert "review_required: true" in text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
