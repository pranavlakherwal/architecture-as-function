"""The plain report behind `python -m a_star measure PATH`.

Seven readings, one line each: what it measures in words, the value with its unit,
where it sits among the repositories we have measured, and whether to act.
Then the top three fixes, each built from the reading's own internals: the files, links
or numbers of the measured repository, never a guess.

The fleet reference (`fleet_reference.json`) holds only sorted numbers, a count and a date.
A reading is marked "act" when it is higher than at least three quarters of those numbers.
Lower is better on every reading: each one is a cost.
"""

from __future__ import annotations

import datetime as _dt
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import TextIO

from .core_vector import (
    CoreVector,
    _walk_files,
    folder_distinctness,
    measure_repo,
    prefix_key,
    relative_links,
    touch_counts,
)

FLEET_REFERENCE_PATH = Path(__file__).with_name("fleet_reference.json")

# The seven readings in the order they are printed. The JSON keeps this order.
READING_KEYS: tuple[str, ...] = (
    "c_find",
    "c_modify",
    "c_storage",
    "c_money",
    "c_drift",
    "c_loss",
    "c_derive",
)

# What each reading measures, in words a reader can say back, and its unit.
LABELS: dict[str, str] = {
    "c_find": "How deep a reader digs to find a file",
    "c_modify": "How often a changed file changes again in a year",
    "c_storage": "How much the repository stores",
    "c_money": "What the system costs to run each month",
    "c_drift": "How many kinds of file the repository mixes",
    "c_loss": "How many links inside the docs point nowhere",
    "c_derive": "How much of what is tracked is a build output",
}

UNITS: dict[str, str] = {
    "c_find": "weighted folder levels",
    "c_modify": "touches per file",
    "c_storage": "bytes",
    "c_money": "USD per month",
    "c_drift": "share of the possible mix, 0 to 1",
    "c_loss": "share of links, 0 to 1",
    "c_derive": "share of tracked files, 0 to 1",
}

# Readings that are stand-ins today. We say so and do not invent a fix from them.
PROXY_KEYS: frozenset[str] = frozenset({"c_money", "c_derive"})

ACT_SHARE = 0.75  # "act" when higher than at least this share of the measured repositories
DEEP_LEVELS = 4  # a file this many folders down or deeper counts as deep in the c_find fix
TOP_N = 5  # how many files, links or types a fix names


# ---- Fleet reference ---------------------------------------------------------


def load_fleet_reference(path: Path = FLEET_REFERENCE_PATH) -> dict | None:
    """Read the fleet reference, or None when it is missing or unreadable."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict) or "n" not in data or "as_of" not in data:
        return None
    return data


def count_below(values: list[float], value: float) -> int:
    """How many fleet values sit strictly below `value`. The fleet list is sorted ascending."""
    # A linear scan keeps the rule obvious; the fleet is a few dozen numbers.
    return sum(1 for v in values if v < value)


def rank(key: str, value: float, fleet: dict | None) -> tuple[str, bool]:
    """The rank sentence and the act flag for one reading against the fleet."""
    if fleet is None or key not in fleet or not fleet.get("n"):
        return ("no fleet reference to compare against", False)
    values = fleet[key]
    n = int(fleet["n"])
    below = count_below(values, value)
    text = f"higher than {below} of {n} measured repos"
    act = (below / n) >= ACT_SHARE if n else False
    return (text, act)


# ---- Internals the fixes are built from -------------------------------------


def _notes(cv: CoreVector, key: str) -> dict[str, str]:
    """The key=value notes of one reading as a dict. Free-text notes are dropped."""
    out: dict[str, str] = {}
    for note in cv.measurements[key].notes:
        if "=" in note and " " not in note.split("=", 1)[0]:
            k, v = note.split("=", 1)
            out[k] = v
    return out


def _rel(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _share(part: float, whole: float) -> str:
    return f"{(100.0 * part / whole):.0f}%" if whole else "0%"


def fix_c_find(root: Path, cv: CoreVector) -> tuple[str, str]:
    files = list(_walk_files(root))
    deep = [f for f in files if len(f.relative_to(root).parts) - 1 >= DEEP_LEVELS]
    by_folder: dict[Path, list[str]] = {}
    for f in files:
        by_folder.setdefault(f.parent, []).append(f.name)
    crowded = []
    for folder, names in by_folder.items():
        if len(names) < 2:
            continue
        d = folder_distinctness(names)
        if d < 1.0:
            ctr = Counter(prefix_key(n) for n in names)
            common, count = ctr.most_common(1)[0]
            crowded.append((d, count, _rel(root, folder) or ".", common or "_"))
    crowded.sort(key=lambda t: (t[0], -t[1], t[2]))
    parts = []
    if deep:
        sample = ", ".join(_rel(root, f) for f in deep[:TOP_N])
        parts.append(f"{len(deep)} of {len(files)} files sit {DEEP_LEVELS} or more folders deep: {sample}.")
    if crowded:
        sample = "; ".join(
            f"{folder} ({count} names start with '{common}')" for _, count, folder, common in crowded[:TOP_N]
        )
        parts.append(f"Folders where sibling names look alike: {sample}.")
    if not parts:
        notes = _notes(cv, "c_find")
        parts.append(
            f"No file is {DEEP_LEVELS} or more folders deep and no folder has look-alike names "
            f"(mean depth {notes.get('mean_depth', '?')})."
        )
    title = (
        "Flatten deep paths and rename look-alike files"
        if (deep or crowded)
        else "Paths are shallow and names distinct"
    )
    return title, " ".join(parts)


def fix_c_modify(root: Path, cv: CoreVector, until: str | None = None) -> tuple[str, str]:
    """`until` is the end of the change window the reading used, so the fix names the same year."""
    ctr = touch_counts(root, until=until)
    window = f"the 365 days ending {until[:10]}" if until else "the last 365 days"
    if not ctr:
        return ("No commit history to read", f"git found no commits in {window}, so there is nothing to split.")
    total = sum(ctr.values())
    top = ctr.most_common(TOP_N)
    top_total = sum(c for _, c in top)
    sample = ", ".join(f"{name} ({count})" for name, count in top)
    detail = (
        f"The {len(top)} most touched files take {top_total} of {total} touches ({_share(top_total, total)}): {sample}. "
        f"Split the ones that change for more than one reason."
    )
    return ("Split the files that take most of the changes", detail)


def fix_c_storage(root: Path, cv: CoreVector) -> tuple[str, str]:
    sizes = []
    for f in _walk_files(root):
        try:
            sizes.append((f.stat().st_size, f))
        except OSError:
            continue
    if not sizes:
        return ("Nothing stored", "The walk found no files.")
    total = sum(s for s, _ in sizes)
    sizes.sort(key=lambda t: (-t[0], t[1].as_posix()))
    top = sizes[:TOP_N]
    top_total = sum(s for s, _ in top)
    sample = ", ".join(f"{_rel(root, f)} ({_human_bytes(s)})" for s, f in top)
    detail = (
        f"The {len(top)} largest files hold {_human_bytes(top_total)} of {_human_bytes(total)} ({_share(top_total, total)}): "
        f"{sample}. Move the ones that are outputs, not sources, out of the repository."
    )
    return ("Move the largest files out", detail)


def fix_c_money(root: Path, cv: CoreVector) -> tuple[str, str]:
    m = cv.measurements["c_money"]
    if m.confidence == "high":
        return (
            "Billing supplied, no fix derived",
            f"Monthly spend given as {m.value:g} USD. One number is not a lineage, so we do not invent a fix from it.",
        )
    return (
        "Monthly cost is a stand-in today",
        "No billing figure was supplied, so this reading is 0 by default. We do not invent a fix from it. "
        "Pass --monthly-usd when you have the number.",
    )


def fix_c_drift(root: Path, cv: CoreVector) -> tuple[str, str]:
    ctr: Counter = Counter()
    examples: dict[str, str] = {}
    for f in _walk_files(root):
        ext = f.suffix.lower() or "<no-ext>"
        ctr[ext] += 1
        examples.setdefault(ext, _rel(root, f))
    if not ctr:
        return ("No files to type", "The walk found no files.")
    total = sum(ctr.values())
    rare = sorted(ctr.items(), key=lambda kv: (kv[1], kv[0]))[:TOP_N]
    sample = ", ".join(f"{ext} ({count}, e.g. {examples[ext]})" for ext, count in rare)
    detail = (
        f"{len(ctr)} file types across {total} files. The rarest: {sample}. "
        f"Each odd type is a tool a new reader has to learn; drop or consolidate the ones nobody runs."
    )
    return ("Cut the odd file types", detail)


def fix_c_loss(root: Path, cv: CoreVector) -> tuple[str, str]:
    links = relative_links(root)
    orphans = [(f, t) for f, t, exists in links if exists is False]
    if not orphans:
        return ("No links point nowhere", f"{len(links)} relative links checked, every one resolves to a file.")
    sample = "; ".join(f"{_rel(root, f)} -> {t}" for f, t in orphans[:TOP_N])
    more = f" and {len(orphans) - TOP_N} more" if len(orphans) > TOP_N else ""
    detail = f"{len(orphans)} of {len(links)} relative links point nowhere: {sample}{more}. Fix the target or remove the link."
    return ("Repair the links that point nowhere", detail)


def fix_c_derive(root: Path, cv: CoreVector) -> tuple[str, str]:
    notes = _notes(cv, "c_derive")
    derived = notes.get("derived_files", "?")
    total = notes.get("total_files", "?")
    return (
        "Build outputs are a stand-in today",
        f"{derived} of {total} tracked files sit in build, dist, generated or cache folders. "
        "This stands in for a real lineage graph, so we do not invent a fix from it.",
    )


FIXES = {
    "c_find": fix_c_find,
    "c_modify": fix_c_modify,
    "c_storage": fix_c_storage,
    "c_money": fix_c_money,
    "c_drift": fix_c_drift,
    "c_loss": fix_c_loss,
    "c_derive": fix_c_derive,
}


def _human_bytes(n: float) -> str:
    n = float(n)
    for unit in ("bytes", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "bytes" else f"{n:.1f} {unit}"
        n /= 1024.0
    return f"{n:.1f} GB"


# ---- Report ------------------------------------------------------------------


def build_report(
    path: Path,
    fleet: dict | None = None,
    as_of: str | None = None,
    monthly_usd: float | None = None,
) -> dict:
    """Measure `path` and return the report as a dict in the published JSON shape.

    With `as_of` (YYYY-MM-DD) the 365 day change window ends at the close of that day and the
    JSON carries the date. The other readings come from the files as they stand on disk.
    """
    root = Path(path).resolve()
    if fleet is None:
        fleet = load_fleet_reference()
    measured_at = None
    if as_of is None:
        as_of = _dt.date.today().isoformat()
    else:
        measured_at = f"{as_of}T23:59:59"
    cv = measure_repo(root, {"monthly_usd": monthly_usd} if monthly_usd is not None else None, measured_at=measured_at)

    readings = []
    shares = []
    for key in READING_KEYS:
        value = float(cv.measurements[key].value)
        text, act = rank(key, value, fleet)
        readings.append(
            {
                "key": key,
                "label": LABELS[key],
                "value": value,
                "unit": UNITS[key],
                "rank_text": text,
                "act": act,
            }
        )
        n = int(fleet["n"]) if fleet and fleet.get("n") else 0
        share = count_below(fleet[key], value) / n if (fleet and key in fleet and n) else 0.0
        shares.append((share, key))

    # Highest share first; ties keep the printed order of the readings.
    order = sorted(range(len(READING_KEYS)), key=lambda i: (-shares[i][0], i))
    fixes = []
    for i in order[:3]:
        key = READING_KEYS[i]
        if key == "c_modify":
            title, detail = fix_c_modify(root, cv, until=measured_at)
        else:
            title, detail = FIXES[key](root, cv)
        fixes.append({"rank": len(fixes) + 1, "title": title, "detail": detail})

    return {
        "path": str(root),
        "as_of": as_of,
        "fleet_n": int(fleet["n"]) if fleet and fleet.get("n") else 0,
        "readings": readings,
        "fixes": fixes,
    }


def _value_text(key: str, value: float) -> str:
    if key == "c_storage":
        return f"{int(value):,} bytes ({_human_bytes(value)})"
    if key == "c_money":
        return f"{value:g} USD per month"
    if key in ("c_drift", "c_loss", "c_derive"):
        return f"{value:.3f} of 1"
    return f"{value:.3f} {UNITS[key]}"


def _long_date(iso: str) -> str:
    try:
        d = _dt.date.fromisoformat(iso)
    except ValueError:
        return iso
    return f"{d.day} {d.strftime('%B %Y')}"


def format_plain(report: dict, fleet: dict | None = None) -> str:
    """Render the report as text: a header, seven lines, then the top three fixes."""
    lines = []
    n = report["fleet_n"]
    fleet_date = _long_date(fleet["as_of"]) if fleet and fleet.get("as_of") else None
    against = (
        f"against {n} repos measured {fleet_date}"
        if (n and fleet_date)
        else ("against no fleet reference" if not n else f"against {n} repos")
    )
    lines.append(f"A* measure: {report['path']}")
    lines.append(f"Read {_long_date(report['as_of'])}, {against}. Lower is better on every line.")
    lines.append("")
    label_w = max(len(r["label"]) for r in report["readings"])
    value_w = max(len(_value_text(r["key"], r["value"])) for r in report["readings"])
    for r in report["readings"]:
        verdict = "act" if r["act"] else "fine"
        lines.append(
            f"{r['label']:<{label_w}}  {_value_text(r['key'], r['value']):<{value_w}}  {r['rank_text']}  {verdict}"
        )
    lines.append("")
    high = sum(1 for r in report["readings"] if r["act"])
    if high >= 3:
        lines.append(f"Top three fixes ({high} readings sit above three quarters of the measured repos)")
    elif high > 0:
        lines.append(
            f"Top three fixes ({high} reading{'s' if high > 1 else ''} sit{'s' if high == 1 else ''} above three quarters "
            f"of the measured repos; the rest are the next by rank)"
        )
    else:
        lines.append(
            "Top three fixes (no reading sits above three quarters of the measured repos; these are the next by rank)"
        )
    for fx in report["fixes"]:
        lines.append(f"{fx['rank']}. {fx['title']}.")
        lines.append(f"   {fx['detail']}")
    return "\n".join(lines) + "\n"


_AS_OF_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


def valid_as_of(text: str) -> bool:
    """True for a real calendar date written YYYY-MM-DD, and for nothing else."""
    if not _AS_OF_RE.fullmatch(text or ""):
        return False
    try:
        _dt.date.fromisoformat(text)
    except ValueError:
        return False
    return True


def run_measure(
    path: Path,
    as_json: bool = False,
    monthly_usd: float | None = None,
    as_of: str | None = None,
    out: TextIO = sys.stdout,
    err: TextIO = sys.stderr,
) -> int:
    """The command body. Returns 0 on success, 2 when `path` is not a directory or `as_of` is not a date."""
    path = Path(path)
    if not path.is_dir():
        print(f"a_star measure: {path} is not a directory", file=err)
        return 2
    if as_of is not None and not valid_as_of(as_of):
        print(f"a_star measure: --as-of wants a date written YYYY-MM-DD, got {as_of}", file=err)
        return 2
    fleet = load_fleet_reference()
    report = build_report(path, fleet=fleet, as_of=as_of, monthly_usd=monthly_usd)
    if as_json:
        out.write(json.dumps(report, indent=2) + "\n")
    else:
        out.write(format_plain(report, fleet=fleet))
    return 0
