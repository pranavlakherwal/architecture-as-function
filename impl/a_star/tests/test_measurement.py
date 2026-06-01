"""C_core measurement smoke tests."""

import subprocess
from pathlib import Path

import pytest

from a_star.measurement import AXIS_SPECS, measure_repo
from a_star.measurement.core_vector import (
    measure_c_derive,
    measure_c_drift,
    measure_c_find,
    measure_c_loss,
    measure_c_storage,
)

CORE_AXES = (
    "c_find",
    "c_modify",
    "c_storage",
    "c_money",
    "c_drift",
    "c_loss",
    "c_derive",
)


def _seed(tmp_path: Path) -> Path:
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "doc.md").write_text("[ok](a/sib.md)\n[bad](does/not/exist.md)\n[also-ok](sib.md)\n")
    (tmp_path / "a" / "sib.md").write_text("hi")
    (tmp_path / "b").mkdir()
    (tmp_path / "b" / "data.json").write_text("{}")
    (tmp_path / "build").mkdir()
    (tmp_path / "build" / "out.bundle.js").write_text("// derived")
    return tmp_path


def test_axis_specs_complete():
    assert set(AXIS_SPECS) == set(CORE_AXES)
    for spec in AXIS_SPECS.values():
        assert spec.unit
        assert spec.source
        assert spec.owner


def test_measure_repo_returns_all_axes(tmp_path: Path):
    cv = measure_repo(_seed(tmp_path))
    assert set(cv.measurements) == set(CORE_AXES)


def test_c_storage_counts_bytes(tmp_path: Path):
    _seed(tmp_path)
    m = measure_c_storage(tmp_path)
    assert m.value > 0
    assert m.confidence == "high"


def test_c_loss_detects_orphan_link(tmp_path: Path):
    _seed(tmp_path)
    m = measure_c_loss(tmp_path)
    # 3 internal links: `a/sib.md` (orphan, resolves to a/a/sib.md), `does/not/exist.md`
    # (orphan), `sib.md` (resolves to a/sib.md which exists). 2/3.
    assert m.value == pytest.approx(2 / 3, abs=0.001)


def test_c_loss_zero_when_no_md(tmp_path: Path):
    (tmp_path / "x.py").write_text("pass")
    m = measure_c_loss(tmp_path)
    assert m.value == 0.0
    assert m.confidence == "low"


def test_c_drift_bounded_zero_to_one(tmp_path: Path):
    _seed(tmp_path)
    m = measure_c_drift(tmp_path)
    assert 0.0 <= m.value <= 1.0


def test_c_derive_counts_build_artifacts(tmp_path: Path):
    _seed(tmp_path)
    m = measure_c_derive(tmp_path)
    assert m.value > 0


def test_c_find_handles_deeply_nested(tmp_path: Path):
    deep = tmp_path / "a" / "b" / "c" / "d" / "e"
    deep.mkdir(parents=True)
    (deep / "leaf.txt").write_text("x")
    m = measure_c_find(tmp_path)
    assert m.value > 0


def test_c_money_low_confidence_without_input(tmp_path: Path):
    cv = measure_repo(tmp_path)
    assert cv.measurements["c_money"].confidence == "low"
    assert cv.measurements["c_money"].value == 0.0


def test_c_money_high_confidence_with_input(tmp_path: Path):
    cv = measure_repo(tmp_path, {"monthly_usd": 42.50})
    assert cv.measurements["c_money"].value == 42.5
    assert cv.measurements["c_money"].confidence == "high"


def test_measure_c_modify_low_confidence_outside_git(tmp_path: Path):
    cv = measure_repo(tmp_path)
    assert cv.measurements["c_modify"].confidence == "low"


def test_values_only_returns_floats(tmp_path: Path):
    _seed(tmp_path)
    cv = measure_repo(tmp_path)
    values = cv.values_only()
    assert set(values) == set(CORE_AXES)
    for v in values.values():
        assert isinstance(v, float)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
