"""Tests for `python -m a_star measure`: the report, the fleet reference and the command."""

from __future__ import annotations

import io
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import pytest
from a_star.measurement import build_fleet_reference as bfr
from a_star.measurement import report as rpt

IMPL = Path(__file__).resolve().parents[2]

# Spelled out, not imported: a dropped reading must fail here even if the module's list shrank too.
SEVEN = ("c_find", "c_modify", "c_storage", "c_money", "c_drift", "c_loss", "c_derive")


def _fleet(n: int = 20, **override: list) -> dict:
    """A fabricated fleet: every reading runs 1..n (c_storage in megabytes) unless overridden."""
    fleet = {"as_of": "2026-11-07", "n": n}
    for key in SEVEN:
        scale = 1_000_000.0 if key == "c_storage" else 1.0
        fleet[key] = override.get(key, [float(i) * scale for i in range(1, n + 1)])
    return fleet


# c_find values where a messy repo clears 16 of 20 and a flat one clears none.
FIND_FLEET = [float(i) / 10 for i in range(1, 17)] + [10.0] * 4
LOSS_FLEET = [0.0] * 15 + [0.1, 0.2, 0.3, 0.4, 0.5]


def _messy_repo(tmp_path: Path) -> Path:
    """World one: deep paths, look-alike names, links that point nowhere."""
    root = tmp_path / "messy"
    deep = root / "a" / "b" / "c" / "d" / "e"
    deep.mkdir(parents=True)
    for i in range(4):
        (deep / f"leaf{i}.txt").write_text("x")
    (root / "docs").mkdir()
    (root / "docs" / "index.md").write_text("[gone](missing/one.md)\n[gone too](missing/two.md)\n[ok](here.md)\n")
    (root / "docs" / "here.md").write_text("hi")
    for i in range(3):
        (root / f"report_{i}.md").write_text(f"[dead {i}](nowhere_{i}.md)\n")
    return root


def _clean_repo(tmp_path: Path) -> Path:
    """World two: flat, distinct names, every link resolves."""
    root = tmp_path / "clean"
    root.mkdir()
    (root / "alpha.md").write_text("[ok](beta.md)\n")
    (root / "beta.md").write_text("hi")
    (root / "gamma.py").write_text("pass\n")
    return root


def _sixty_file_repo(tmp_path: Path) -> Path:
    root = tmp_path / "sixty"
    for i in range(60):
        folder = root / f"part{i % 6}"
        folder.mkdir(parents=True, exist_ok=True)
        suffix = (".py", ".md", ".json", ".txt")[i % 4]
        body = f"[link](../part{(i + 1) % 6}/file{i}.md)\n" if suffix == ".md" else "x" * (i + 1)
        (folder / f"file{i}{suffix}").write_text(body)
    return root


# ---- JSON shape ---------------------------------------------------------------


def test_json_shape_is_exact(tmp_path: Path):
    report = rpt.build_report(_clean_repo(tmp_path), fleet=_fleet(), as_of="2026-11-07")
    assert set(report) == {"path", "as_of", "fleet_n", "readings", "fixes"}
    assert isinstance(report["path"], str)
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", report["as_of"])
    assert isinstance(report["fleet_n"], int) and report["fleet_n"] == 20
    for r in report["readings"]:
        assert set(r) == {"key", "label", "value", "unit", "rank_text", "act"}
        assert isinstance(r["value"], float)
        assert isinstance(r["act"], bool)
        assert r["label"] and r["unit"] and r["rank_text"]
    for fx in report["fixes"]:
        assert set(fx) == {"rank", "title", "detail"}
        assert isinstance(fx["rank"], int)
        assert fx["title"] and fx["detail"]
    json.dumps(report)  # the whole thing serialises


def test_readings_are_the_seven_in_order(tmp_path: Path):
    report = rpt.build_report(_clean_repo(tmp_path), fleet=_fleet(), as_of="2026-11-07")
    assert tuple(r["key"] for r in report["readings"]) == SEVEN


def test_exactly_three_fixes_ranked_one_to_three(tmp_path: Path):
    report = rpt.build_report(_clean_repo(tmp_path), fleet=_fleet(), as_of="2026-11-07")
    assert [fx["rank"] for fx in report["fixes"]] == [1, 2, 3]


# ---- Rank and act ---------------------------------------------------------------


def test_rank_counts_fleet_values_strictly_below():
    fleet = _fleet(20)
    assert rpt.rank("c_find", 21.0, fleet) == ("higher than 20 of 20 measured repos", True)
    assert rpt.rank("c_find", 0.0, fleet) == ("higher than 0 of 20 measured repos", False)
    assert rpt.rank("c_find", 1.0, fleet) == ("higher than 0 of 20 measured repos", False)  # a tie is not "higher"


def test_act_means_higher_than_three_quarters():
    fleet = _fleet(20)
    text, act = rpt.rank("c_loss", 16.0, fleet)  # 15 below, 15/20 = 0.75
    assert text == "higher than 15 of 20 measured repos" and act is True
    text, act = rpt.rank("c_loss", 15.0, fleet)  # 14 below, 0.70
    assert text == "higher than 14 of 20 measured repos" and act is False


def test_no_fleet_means_no_rank_and_no_act(tmp_path: Path):
    report = rpt.build_report(_clean_repo(tmp_path), fleet={"as_of": "2026-11-07", "n": 0}, as_of="2026-11-07")
    assert report["fleet_n"] == 0
    assert all(r["act"] is False for r in report["readings"])
    assert all("no fleet reference" in r["rank_text"] for r in report["readings"])


# ---- Two worlds -----------------------------------------------------------------


def test_two_worlds_act_flags_differ(tmp_path: Path):
    # Fleet values sit where a messy repo clears them and a clean one does not.
    fleet = _fleet(20, c_loss=LOSS_FLEET, c_find=FIND_FLEET)
    messy = rpt.build_report(_messy_repo(tmp_path), fleet=fleet, as_of="2026-11-07")
    clean = rpt.build_report(_clean_repo(tmp_path), fleet=fleet, as_of="2026-11-07")
    m = {r["key"]: r for r in messy["readings"]}
    c = {r["key"]: r for r in clean["readings"]}
    assert m["c_loss"]["value"] == pytest.approx(5 / 6, abs=0.001)  # the reading rounds to four places
    assert m["c_loss"]["act"] is True and c["c_loss"]["act"] is False
    assert m["c_find"]["act"] is True and c["c_find"]["act"] is False
    assert c["c_loss"]["value"] == 0.0


def test_two_worlds_fixes_name_the_repo_own_files(tmp_path: Path):
    fleet = _fleet(20, c_loss=LOSS_FLEET, c_find=FIND_FLEET)
    messy = rpt.build_report(_messy_repo(tmp_path), fleet=fleet, as_of="2026-11-07")
    clean = rpt.build_report(_clean_repo(tmp_path), fleet=fleet, as_of="2026-11-07")
    messy_text = " ".join(fx["title"] + " " + fx["detail"] for fx in messy["fixes"])
    clean_text = " ".join(fx["title"] + " " + fx["detail"] for fx in clean["fixes"])
    # The two high readings lead the messy list and their details carry the real paths and links.
    assert messy["fixes"][0]["title"] == "Repair the links that point nowhere"
    assert "docs/index.md -> missing/one.md" in messy_text
    assert "a/b/c/d/e/leaf0.txt" in messy_text
    assert "5 of 6 relative links point nowhere" in messy_text
    assert [fx["title"] for fx in messy["fixes"][:2]] == [
        "Repair the links that point nowhere",
        "Flatten deep paths and rename look-alike files",
    ]
    # The clean world has nothing of the sort.
    assert "point nowhere" not in clean_text
    assert "leaf0" not in clean_text
    assert "Paths are shallow and names distinct" in clean_text
    assert messy["fixes"] != clean["fixes"]


def test_fixes_follow_rank_not_reading_order(tmp_path: Path):
    # Only c_drift clears the fleet; it must come first even though it is fifth in reading order.
    root = _clean_repo(tmp_path)
    huge = [1000.0] * 20
    fleet = _fleet(
        20, c_find=huge, c_modify=huge, c_storage=huge, c_money=huge, c_loss=huge, c_derive=huge, c_drift=[0.0] * 20
    )
    report = rpt.build_report(root, fleet=fleet, as_of="2026-11-07")
    acts = [r["key"] for r in report["readings"] if r["act"]]
    assert acts == ["c_drift"]
    assert report["fixes"][0]["title"] == "Cut the odd file types"
    # The remaining two are the next in reading order, since every other share is zero.
    assert [fx["title"] for fx in report["fixes"][1:]] == [
        "Paths are shallow and names distinct",
        "No commit history to read",
    ]


def test_proxy_readings_say_so_and_invent_no_fix(tmp_path: Path):
    root = _clean_repo(tmp_path)
    huge = [1000.0] * 20
    fleet = _fleet(20, c_find=huge, c_modify=huge, c_storage=huge, c_money=huge, c_loss=huge, c_drift=huge)
    fleet["c_derive"] = [-1.0] * 20  # anything clears it
    report = rpt.build_report(root, fleet=fleet, as_of="2026-11-07")
    first = report["fixes"][0]
    assert first["title"] == "Build outputs are a stand-in today"
    assert "do not invent a fix" in first["detail"]


# ---- Plain text -------------------------------------------------------------------


def test_plain_text_has_seven_reading_lines_and_three_fixes(tmp_path: Path):
    fleet = _fleet()
    report = rpt.build_report(_clean_repo(tmp_path), fleet=fleet, as_of="2026-11-07")
    text = rpt.format_plain(report, fleet=fleet)
    reading_lines = [ln for ln in text.splitlines() if "higher than" in ln and "measured repos" in ln]
    assert len(reading_lines) == 7
    for ln in reading_lines:
        assert ln.endswith(" fine") or ln.endswith(" act")
    assert "Top three fixes" in text
    assert "\n1. " in text and "\n2. " in text and "\n3. " in text
    assert "Read 7 November 2026, against 20 repos measured 7 November 2026" in text
    for bad in ("—", "–"):
        assert bad not in text


# ---- Speed ------------------------------------------------------------------------


def test_under_one_second_on_sixty_files(tmp_path: Path):
    root = _sixty_file_repo(tmp_path)
    fleet = _fleet()
    start = time.perf_counter()
    report = rpt.build_report(root, fleet=fleet, as_of="2026-11-07")
    rpt.format_plain(report, fleet=fleet)
    elapsed = time.perf_counter() - start
    assert elapsed < 1.0, f"took {elapsed:.2f}s"


# ---- Fleet reference file -----------------------------------------------------------


def _assert_reference_shape(data: dict):
    assert set(data) == {"as_of", "n", *SEVEN}
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", data["as_of"])
    assert isinstance(data["n"], int) and not isinstance(data["n"], bool) and data["n"] >= 1
    for key in SEVEN:
        values = data[key]
        assert isinstance(values, list) and len(values) == data["n"]
        for v in values:
            assert isinstance(v, (int, float)) and not isinstance(v, bool)
        assert values == sorted(values)


def test_shipped_fleet_reference_holds_only_numbers_and_two_fields():
    data = json.loads(rpt.FLEET_REFERENCE_PATH.read_text(encoding="utf-8"))
    _assert_reference_shape(data)

    # Nothing that could name a repository: no string anywhere but the date.
    def strings(obj):
        if isinstance(obj, str):
            yield obj
        elif isinstance(obj, dict):
            for k, v in obj.items():
                yield k
                yield from strings(v)
        elif isinstance(obj, list):
            for v in obj:
                yield from strings(v)

    found = set(strings(data))
    assert found == {"as_of", "n", *SEVEN, data["as_of"]}


def test_build_reference_ships_only_numbers():
    vectors = [{k: float(i) for k in SEVEN} for i in (3, 1, 2)]
    data = bfr.build_reference(vectors, "2026-11-07")
    _assert_reference_shape(data)
    assert data["n"] == 3
    assert data["c_find"] == [1.0, 2.0, 3.0]


def test_discover_repos_depth_and_skips(tmp_path: Path):
    def repo(*parts):
        p = tmp_path.joinpath(*parts)
        (p / ".git").mkdir(parents=True)
        return p

    one = repo("one")
    two = repo("group", "two")
    repo("one", "nested")  # inside a repo found at depth 1: not searched
    repo("group", "deeper", "three")  # depth 3: out of range
    repo("node_modules", "pkg")
    repo("_archives", "old")
    repo("_archive", "older")
    repo("site-backup", "x")
    repo("group", "lane-worktree")
    (tmp_path / "group" / "plain").mkdir()  # a folder that is not a repo
    found = bfr.discover_repos(tmp_path)
    assert found == sorted([one, two])


def test_measure_all_skips_a_repo_that_errors(tmp_path: Path, monkeypatch):
    good = _clean_repo(tmp_path)
    bad = tmp_path / "bad"
    bad.mkdir()
    real = bfr.measure_repo

    def flaky(root, *a, **k):
        if root == bad:
            raise RuntimeError("cannot read")
        return real(root, *a, **k)

    monkeypatch.setattr(bfr, "measure_repo", flaky)
    vectors, skipped = bfr.measure_all([good, bad], err=io.StringIO())
    assert skipped == 1 and len(vectors) == 1
    assert set(vectors[0]) == set(SEVEN)


def test_measure_all_skips_a_repo_over_its_time_budget(tmp_path: Path, monkeypatch):
    import time as _time

    good = _clean_repo(tmp_path)
    slow = tmp_path / "slow"
    slow.mkdir()
    real = bfr.measure_repo

    def sleepy(root, *a, **k):
        if root == slow:
            _time.sleep(2.0)
        return real(root, *a, **k)

    monkeypatch.setattr(bfr, "measure_repo", sleepy)
    vectors, skipped = bfr.measure_all([slow, good], err=io.StringIO(), per_repo_seconds=0.2)
    assert skipped == 1 and len(vectors) == 1


# ---- The command --------------------------------------------------------------------


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "a_star", *args],
        cwd=IMPL,
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_command_rejects_a_path_that_is_not_a_directory(tmp_path: Path):
    f = tmp_path / "file.txt"
    f.write_text("x")
    for target in (f, tmp_path / "does-not-exist"):
        proc = _run("measure", str(target))
        assert proc.returncode != 0
        assert "is not a directory" in proc.stderr
        assert proc.stdout == ""


def test_command_json_matches_shape(tmp_path: Path):
    proc = _run("measure", str(_clean_repo(tmp_path)), "--json")
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert set(data) == {"path", "as_of", "fleet_n", "readings", "fixes"}
    assert [r["key"] for r in data["readings"]] == list(SEVEN)
    assert data["fleet_n"] >= 1  # the shipped fleet reference is loaded


def test_command_plain_prints_seven_lines(tmp_path: Path):
    proc = _run("measure", str(_clean_repo(tmp_path)))
    assert proc.returncode == 0, proc.stderr
    assert sum(1 for ln in proc.stdout.splitlines() if "higher than" in ln and "measured repos" in ln) == 7


def test_main_module_file_exists():
    assert (IMPL / "a_star" / "__main__.py").is_file()
