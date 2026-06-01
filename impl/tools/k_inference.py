"""K-class inference classifier (RQ11 worked implementation).

Walks a repo, extracts observable folder facts, and scores them against
prototype features for each of the 7 K classes defined in A* v0.1.

The 7 K classes:
    1. outbound-pipeline   (cold email / lead-gen)
    2. content-pipeline    (editorial publishing)
    3. product-marketing   (campaign / creative ops)
    4. product-saas        (multi-tenant SaaS app)
    5. research-memory     (knowledge / personal context)
    6. audit-pipeline      (review / audit workflows)
    7. intel-pipeline      (intelligence / ingest engine)

Usage:
    python k_inference.py --root /path/to/repo
    python k_inference.py --root /path/to/repo --explain

Spec: /architecture-as-function/research/open/RQ11_inverse_classifier.md
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

# ---- K class taxonomy --------------------------------------------------------

K_CLASSES: tuple[str, ...] = (
    "outbound-pipeline",
    "content-pipeline",
    "product-marketing",
    "product-saas",
    "research-memory",
    "audit-pipeline",
    "intel-pipeline",
)

# ---- Walk knobs --------------------------------------------------------------

# Directories we never descend into. Keeps walk fast and noise-free.
SKIP_DIRS: frozenset[str] = frozenset(
    {
        ".git",
        ".venv",
        "venv",
        "env",
        "node_modules",
        "__pycache__",
        ".mypy_cache",
        ".pytest_cache",
        ".next",
        "dist",
        "build",
        ".turbo",
        ".cache",
        ".idea",
        ".vscode",
        "playwright-report",
        "test-results",
        ".DS_Store",
    }
)

# Cap so very large repos don't blow up the walk.
MAX_FILES = 20000

# ---- Feature extraction ------------------------------------------------------


@dataclass
class RepoFeatures:
    """Observable facts extracted from a folder walk."""

    root: str
    total_files: int
    max_depth: int
    avg_fanout: float
    ext_histogram: dict[str, int]
    presence: dict[str, bool]
    filename_hits: dict[str, int]

    def as_dict(self) -> dict:
        return {
            "root": self.root,
            "total_files": self.total_files,
            "max_depth": self.max_depth,
            "avg_fanout": round(self.avg_fanout, 2),
            "ext_histogram_top10": dict(
                Counter(self.ext_histogram).most_common(10)
            ),
            "presence": self.presence,
            "filename_hits": self.filename_hits,
        }


# Presence flags. Each is a list of substrings; presence = any match
# in any directory or top-level filename anywhere in the tree.
PRESENCE_PATTERNS: dict[str, tuple[str, ...]] = {
    "dotenv": (".env",),
    "secrets_dir": ("secrets/", "/secrets"),
    "migrations": ("migrations/", "/migrations"),
    "tests": ("tests/", "/tests", "test/"),
    "dist": ("dist/", "/dist", "build/"),
    "frontend": ("web/", "/web", "app/", "frontend/", "/frontend"),
    "articles": ("articles/", "posts/", "content/", "drafts/"),
    "agents": ("agents/", "/agents"),
    "prompts": ("prompts/", "/prompts"),
    "manifests": ("manifests/", "/manifests", "manifest.json", "manifest.yaml"),
    "supabase": ("supabase/", "/supabase"),
    "package_json": ("package.json",),
    "pyproject": ("pyproject.toml", "requirements.txt"),
    "schemas": ("schemas/", "/schemas"),
    "rls_or_rbac": ("rls", "rbac"),
    "memory_dir": ("memory/", "/memory"),
    "leads_dir": ("leads/", "sequences/", "/sequences"),
    "creatives_dir": ("creatives/", "/creatives", "ads/", "/ads", "campaigns/"),
    "audit_dir": ("audit/", "/audits", "review/", "reviews/", "findings/"),
    "ingest_dir": ("ingest/", "scrapers/", "scraper/", "fetchers/"),
}

# Filename keyword regexes. Each pattern is counted across all paths.
FILENAME_PATTERNS: dict[str, re.Pattern[str]] = {
    "outbound_kw": re.compile(
        r"(email|sequence|smartlead|outbound|cold|lead|drip|cadence)", re.I
    ),
    "content_kw": re.compile(
        r"(article|publish|topic|draft|substack|wordpress|seo|geo|aeo)", re.I
    ),
    "marketing_kw": re.compile(
        r"(campaign|creative|brand|persona|ugc|reels|story|carousel|ad[_\-\.]?set)",
        re.I,
    ),
    "saas_kw": re.compile(
        r"(tenant|rls|rbac|role|auth|migration|edge[_\-]?function|user[_\-]?management)",
        re.I,
    ),
    "memory_kw": re.compile(
        r"(memory|context|persona|recall|reflection|episode|twin)", re.I
    ),
    "audit_kw": re.compile(
        r"(audit|review|sop|finding|rule|panel|compliance|attest)", re.I
    ),
    "intel_kw": re.compile(
        r"(ingest|enrich|scrape|harvest|crawl|signal|observer|briefing)", re.I
    ),
}


def extract_features(root: str) -> RepoFeatures:
    """Walk `root` and produce a RepoFeatures snapshot."""

    root_path = Path(root).expanduser().resolve()
    if not root_path.exists():
        raise FileNotFoundError(f"root does not exist: {root_path}")
    if not root_path.is_dir():
        raise NotADirectoryError(f"root is not a directory: {root_path}")

    ext_hist: Counter[str] = Counter()
    presence: dict[str, bool] = {k: False for k in PRESENCE_PATTERNS}
    filename_hits: dict[str, int] = {k: 0 for k in FILENAME_PATTERNS}

    total_files = 0
    max_depth = 0
    fanouts: list[int] = []
    root_str = str(root_path)
    root_depth = root_str.count(os.sep)
    truncated = False

    for dirpath, dirnames, filenames in os.walk(root_path):
        # In-place prune so os.walk skips our skip set.
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]

        depth = dirpath.count(os.sep) - root_depth
        if depth > max_depth:
            max_depth = depth
        fanouts.append(len(dirnames) + len(filenames))

        # Presence: scan the directory path itself.
        dpath_lower = dirpath.lower() + "/"
        for key, patterns in PRESENCE_PATTERNS.items():
            if presence[key]:
                continue
            for p in patterns:
                if p in dpath_lower:
                    presence[key] = True
                    break

        for fname in filenames:
            total_files += 1
            if total_files > MAX_FILES:
                truncated = True
                break

            fname_lower = fname.lower()
            full_lower = (dirpath + "/" + fname).lower()

            # Extension histogram.
            ext = Path(fname).suffix.lower()
            if ext:
                ext_hist[ext] += 1
            else:
                ext_hist["<noext>"] += 1

            # Presence: scan filename too.
            for key, patterns in PRESENCE_PATTERNS.items():
                if presence[key]:
                    continue
                for p in patterns:
                    if p in full_lower:
                        presence[key] = True
                        break

            # Filename keyword hits.
            for key, pat in FILENAME_PATTERNS.items():
                if pat.search(fname_lower):
                    filename_hits[key] += 1

        if truncated:
            break

    avg_fanout = sum(fanouts) / len(fanouts) if fanouts else 0.0

    return RepoFeatures(
        root=str(root_path),
        total_files=min(total_files, MAX_FILES),
        max_depth=max_depth,
        avg_fanout=avg_fanout,
        ext_histogram=dict(ext_hist),
        presence=presence,
        filename_hits=filename_hits,
    )


# ---- Prototype profiles ------------------------------------------------------

# Each prototype encodes:
#   "presence":  presence-flag -> weight (positive = expected, negative = anti)
#   "filename":  filename-pattern -> weight (per-hit, with saturation)
#   "ext":       extension -> weight (per-hit / total_files share)
#   "exclude":   presence flags that strongly disqualify this K
#
# Weights are calibrated by hand from inspection of the seed projects.

PROTOTYPES: dict[str, dict] = {
    "outbound-pipeline": {
        "presence": {
            "leads_dir": 3.0,
            "agents": 1.0,
            "dotenv": 0.5,
            "tests": 0.5,
        },
        "filename": {
            "outbound_kw": 0.8,
        },
        "ext": {
            ".py": 0.4,
            ".csv": 0.6,
            ".yaml": 0.3,
            ".yml": 0.3,
            ".json": 0.2,
        },
        "exclude": {"supabase", "articles"},
    },
    "content-pipeline": {
        "presence": {
            "articles": 3.0,
            "agents": 1.0,
            "prompts": 0.8,
            "tests": 0.4,
        },
        "filename": {
            "content_kw": 0.8,
        },
        "ext": {
            ".md": 0.6,
            ".mdx": 0.6,
            ".js": 0.2,
            ".ts": 0.2,
            ".astro": 0.3,
        },
        "exclude": {"leads_dir"},
    },
    "product-marketing": {
        "presence": {
            "creatives_dir": 3.0,
            "frontend": 0.5,
        },
        "filename": {
            "marketing_kw": 0.9,
        },
        "ext": {
            ".png": 0.4,
            ".jpg": 0.4,
            ".jpeg": 0.4,
            ".mp4": 0.6,
            ".mov": 0.6,
            ".psd": 0.6,
            ".ai": 0.6,
        },
        "exclude": {"migrations"},
    },
    "product-saas": {
        "presence": {
            "supabase": 3.0,
            "migrations": 2.0,
            "frontend": 1.5,
            "tests": 0.6,
            "package_json": 0.6,
            "dist": 0.3,
            "rls_or_rbac": 1.5,
        },
        "filename": {
            "saas_kw": 0.5,
        },
        "ext": {
            ".tsx": 0.5,
            ".ts": 0.3,
            ".sql": 0.6,
            ".html": 0.2,
            ".css": 0.2,
        },
        "exclude": {},
    },
    "research-memory": {
        "presence": {
            "memory_dir": 3.0,
            "agents": 0.8,
        },
        "filename": {
            "memory_kw": 0.8,
        },
        "ext": {
            ".md": 0.7,
            ".json": 0.3,
            ".yaml": 0.2,
        },
        "exclude": {"supabase", "creatives_dir"},
    },
    "audit-pipeline": {
        "presence": {
            "audit_dir": 2.5,
            "agents": 0.8,
            "tests": 0.6,
            "schemas": 0.6,
        },
        "filename": {
            "audit_kw": 0.9,
        },
        "ext": {
            ".py": 0.4,
            ".yaml": 0.4,
            ".yml": 0.4,
            ".json": 0.2,
            ".docx": 0.3,
            ".pdf": 0.2,
        },
        "exclude": {"creatives_dir", "leads_dir"},
    },
    "intel-pipeline": {
        "presence": {
            "ingest_dir": 2.5,
            "schemas": 1.0,
            "agents": 0.8,
            "tests": 0.6,
        },
        "filename": {
            "intel_kw": 1.0,
        },
        "ext": {
            ".py": 0.4,
            ".yaml": 0.5,
            ".yml": 0.5,
            ".json": 0.3,
            ".jsonl": 0.7,
        },
        "exclude": {"creatives_dir", "leads_dir"},
    },
}


# ---- Scoring ----------------------------------------------------------------

# Cap on per-feature contribution so a 5000-file dump can't drown signal.
SATURATION = 50


def _sat(x: float) -> float:
    """Soft saturation: x small -> ~x; x large -> ~SATURATION."""
    return SATURATION * x / (SATURATION + x) if x >= 0 else x


@dataclass
class Score:
    k_class: str
    score: float
    raw_contributions: dict[str, float] = field(default_factory=dict)


def score_features(features: RepoFeatures) -> list[Score]:
    """Score features against all K prototypes, return list sorted desc."""

    total = max(features.total_files, 1)
    results: list[Score] = []

    for k_name, proto in PROTOTYPES.items():
        contribs: dict[str, float] = {}
        score = 0.0

        # Presence contributions.
        for flag, weight in proto.get("presence", {}).items():
            if features.presence.get(flag):
                contribs[f"presence:{flag}"] = weight
                score += weight

        # Filename keyword contributions (saturated).
        for kw, weight in proto.get("filename", {}).items():
            hits = features.filename_hits.get(kw, 0)
            if hits > 0:
                contrib = weight * _sat(hits)
                contribs[f"filename:{kw}:{hits}hits"] = contrib
                score += contrib

        # Extension share contributions (share of total files * weight * 100).
        for ext, weight in proto.get("ext", {}).items():
            count = features.ext_histogram.get(ext, 0)
            if count > 0:
                share = count / total
                contrib = weight * share * 100.0
                contribs[f"ext:{ext}:{count}files({share:.1%})"] = contrib
                score += contrib

        # Excludes: subtract a flat penalty when present.
        for flag in proto.get("exclude", set()):
            if features.presence.get(flag):
                penalty = -1.5
                contribs[f"exclude:{flag}"] = penalty
                score += penalty

        results.append(
            Score(k_class=k_name, score=round(score, 3), raw_contributions=contribs)
        )

    results.sort(key=lambda s: s.score, reverse=True)
    return results


def top_k_with_confidence(
    scores: list[Score], k: int = 3
) -> list[tuple[str, float, float]]:
    """Return [(class, score, confidence)] for top k.

    Confidence = softmax-ish: score_i / sum(max(0, score_j)). Pure ordering
    aid, not a probability.
    """
    top = scores[:k]
    pos_total = sum(max(0.0, s.score) for s in scores)
    if pos_total <= 0:
        return [(s.k_class, s.score, 0.0) for s in top]
    return [
        (s.k_class, s.score, round(max(0.0, s.score) / pos_total, 3)) for s in top
    ]


# ---- CLI --------------------------------------------------------------------


def classify(root: str) -> dict:
    """Top-level: extract + score, return JSON-ready result."""
    features = extract_features(root)
    scores = score_features(features)
    top3 = top_k_with_confidence(scores, k=3)
    return {
        "root": features.root,
        "features": features.as_dict(),
        "scores": [
            {"k": s.k_class, "score": s.score, "contributions": s.raw_contributions}
            for s in scores
        ],
        "top3": [
            {"k": k, "score": s, "confidence": c} for (k, s, c) in top3
        ],
        "prediction": top3[0][0] if top3 else None,
    }


def _format_explain(result: dict) -> str:
    lines: list[str] = []
    lines.append(f"# K-inference for {result['root']}")
    lines.append("")
    f = result["features"]
    lines.append(
        f"Files: {f['total_files']}  max_depth: {f['max_depth']}  "
        f"avg_fanout: {f['avg_fanout']}"
    )
    lines.append(f"Top extensions: {f['ext_histogram_top10']}")
    present = [k for k, v in f["presence"].items() if v]
    lines.append(f"Presence flags ON: {present}")
    hits = {k: v for k, v in f["filename_hits"].items() if v > 0}
    lines.append(f"Filename hits: {hits}")
    lines.append("")
    lines.append("## Top-3 predictions")
    for entry in result["top3"]:
        lines.append(
            f"  {entry['k']:22s}  score={entry['score']:>7.2f}  "
            f"conf={entry['confidence']:.2f}"
        )
    lines.append("")
    lines.append("## Why (top-1 contributions)")
    top1 = result["scores"][0]
    for name, val in sorted(
        top1["contributions"].items(), key=lambda kv: -abs(kv[1])
    ):
        lines.append(f"  {val:+7.2f}  {name}")
    return "\n".join(lines)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="A* K-class inference classifier")
    parser.add_argument("--root", required=True, help="Path to the repo to classify")
    parser.add_argument(
        "--explain", action="store_true", help="Print a readable explanation"
    )
    parser.add_argument(
        "--json", action="store_true", help="Print full result as JSON"
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        result = classify(args.root)
    except (FileNotFoundError, NotADirectoryError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    elif args.explain:
        print(_format_explain(result))
    else:
        # Default: terse top-3 line.
        for entry in result["top3"]:
            print(
                f"{entry['k']:22s}  score={entry['score']:>7.2f}  "
                f"conf={entry['confidence']:.2f}"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
