"""Tests for tools/k_inference.py — the RQ11 worked classifier.

Strategy:
- Build small synthetic fixture folders for each K class.
- Assert top-1 prediction matches the expected K.
- Also exercise the feature extractor and the explain formatter.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# Make tools/ importable.
HERE = Path(__file__).resolve().parent
IMPL_ROOT = HERE.parent
sys.path.insert(0, str(IMPL_ROOT))

from tools import k_inference  # noqa: E402
from tools.k_inference import (  # noqa: E402
    K_CLASSES,
    PROTOTYPES,
    classify,
    extract_features,
    score_features,
    top_k_with_confidence,
)


# ---- Fixture builders -------------------------------------------------------


def _touch(p: Path, content: str = "") -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content or "x\n")


def make_outbound_repo(root: Path) -> Path:
    _touch(root / ".env", "SMARTLEAD_API_KEY=xxx\n")
    _touch(root / "leads" / "C9_leads.csv", "email,name\n")
    _touch(root / "sequences" / "build_c6_sequences.py", "# outbound\n")
    _touch(root / "agents" / "smartlead_agent.py", "# agent\n")
    _touch(root / "tests" / "test_sequences.py", "def test(): pass\n")
    _touch(root / "config.yaml", "smartlead: true\n")
    return root


def make_content_repo(root: Path) -> Path:
    for slug in ("rapamycin", "autophagy", "glp1"):
        _touch(root / "articles" / f"{slug}.md", f"# {slug}\n")
    _touch(root / "agents" / "lsd_draft.js", "// draft agent\n")
    _touch(root / "prompts" / "article_outline.md", "outline\n")
    _touch(root / "scripts" / "publish.js", "// publish\n")
    _touch(root / "drafts" / "topic_research.md", "topic notes\n")
    return root


def make_marketing_repo(root: Path) -> Path:
    _touch(root / "creatives" / "static_1.png", "binary\n")
    _touch(root / "creatives" / "video_reel.mp4", "binary\n")
    _touch(root / "campaigns" / "heirloom_campaign.yaml", "ad_set:\n")
    _touch(root / "ads" / "ad_set_lal.json", "{}\n")
    _touch(root / "brand" / "persona.md", "persona\n")
    _touch(root / "creatives" / "carousel.psd", "binary\n")
    return root


def make_saas_repo(root: Path) -> Path:
    _touch(root / "supabase" / "config.toml", "project_id='x'\n")
    _touch(root / "supabase" / "migrations" / "001_rls.sql", "-- rls policy\n")
    _touch(root / "supabase" / "migrations" / "002_rbac.sql", "-- role table\n")
    _touch(root / "web" / "src" / "App.tsx", "export default ()=>null\n")
    _touch(root / "web" / "package.json", '{"name":"x"}\n')
    _touch(root / "tests" / "test_auth.spec.ts", "// auth\n")
    _touch(root / "dist" / "index.html", "<html></html>\n")
    return root


def make_memory_repo(root: Path) -> Path:
    _touch(root / "memory" / "MEMORY.md", "# memory index\n")
    for proj in ("project_a.md", "project_b.md", "project_c.md"):
        _touch(root / "memory" / "projects" / proj, "# notes\n")
    _touch(root / "agents" / "reflect_agent.md", "reflect\n")
    _touch(root / "context.json", "{}\n")
    _touch(root / "personas" / "twin_persona.md", "persona\n")
    return root


def make_audit_repo(root: Path) -> Path:
    _touch(root / "audits" / "macau_review.docx", "binary\n")
    _touch(root / "reviews" / "panel_completeness.py", "# audit panel\n")
    _touch(root / "findings" / "f001_finding.yaml", "rule_id: GS-1\n")
    _touch(root / "agents" / "sheetal_gs.py", "# rule engine\n")
    _touch(root / "schemas" / "finding_schema.json", "{}\n")
    _touch(root / "tests" / "test_rules.py", "def test(): pass\n")
    _touch(root / "rules" / "rule_001.yaml", "id: 1\n")
    return root


def make_intel_repo(root: Path) -> Path:
    _touch(root / "ingest" / "harvest_briefings.py", "# briefing harvest\n")
    _touch(root / "scrapers" / "tier1_scraper.py", "# scrape\n")
    _touch(root / "data" / "raw_events" / "2026-05-22" / "source.jsonl", "{}\n")
    _touch(root / "schemas" / "raw_event.yaml", "version: 1\n")
    _touch(root / "agents" / "briefing_harvest.py", "# agent\n")
    _touch(root / "tests" / "test_ingest.py", "def test(): pass\n")
    _touch(root / "config.yaml", "sources: []\n")
    return root


FIXTURE_BUILDERS = {
    "outbound-pipeline": make_outbound_repo,
    "content-pipeline": make_content_repo,
    "product-marketing": make_marketing_repo,
    "product-saas": make_saas_repo,
    "research-memory": make_memory_repo,
    "audit-pipeline": make_audit_repo,
    "intel-pipeline": make_intel_repo,
}


# ---- Tests -------------------------------------------------------------------


def test_prototypes_cover_all_seven_k_classes():
    """Every K class in the taxonomy must have a prototype."""
    assert set(PROTOTYPES.keys()) == set(K_CLASSES)
    assert len(PROTOTYPES) == 7


def test_extract_features_basic(tmp_path):
    """Feature extractor returns the expected shape and counts files."""
    repo = make_outbound_repo(tmp_path / "outbound")
    feats = extract_features(str(repo))
    assert feats.total_files >= 5
    assert feats.max_depth >= 1
    assert ".py" in feats.ext_histogram
    assert ".csv" in feats.ext_histogram
    assert feats.presence["leads_dir"] is True
    assert feats.presence["agents"] is True
    assert feats.presence["dotenv"] is True
    assert feats.filename_hits["outbound_kw"] >= 1


@pytest.mark.parametrize("expected_k", list(K_CLASSES))
def test_classifier_top1_on_synthetic_fixtures(tmp_path, expected_k):
    """Each synthetic prototype repo classifies to its own K (top-1)."""
    builder = FIXTURE_BUILDERS[expected_k]
    repo = builder(tmp_path / expected_k)
    result = classify(str(repo))
    assert result["prediction"] == expected_k, (
        f"expected top-1 {expected_k}, got top3="
        f"{[(t['k'], t['score']) for t in result['top3']]}"
    )


def test_top3_contains_correct_class_for_all_fixtures(tmp_path):
    """Top-3 must always contain the ground truth for synthetic fixtures."""
    for expected_k, builder in FIXTURE_BUILDERS.items():
        repo = builder(tmp_path / expected_k)
        result = classify(str(repo))
        top3_classes = [t["k"] for t in result["top3"]]
        assert expected_k in top3_classes, (
            f"{expected_k} not in top3 {top3_classes}"
        )


def test_scoring_is_deterministic_and_sorted(tmp_path):
    """score_features must return a list sorted descending by score."""
    repo = make_audit_repo(tmp_path / "audit")
    feats = extract_features(str(repo))
    scores = score_features(feats)
    assert len(scores) == 7
    score_vals = [s.score for s in scores]
    assert score_vals == sorted(score_vals, reverse=True)


def test_confidence_sums_to_at_most_one(tmp_path):
    """Confidence values should never exceed 1 (sum across top-3)."""
    repo = make_content_repo(tmp_path / "content")
    feats = extract_features(str(repo))
    scores = score_features(feats)
    top3 = top_k_with_confidence(scores, k=3)
    conf_sum = sum(c for (_, _, c) in top3)
    assert 0.0 <= conf_sum <= 1.0 + 1e-9


def test_missing_root_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        extract_features(str(tmp_path / "does_not_exist"))


def test_explain_formatter_runs(tmp_path):
    """The --explain formatter should produce a non-empty string."""
    repo = make_saas_repo(tmp_path / "saas")
    result = classify(str(repo))
    text = k_inference._format_explain(result)
    assert "Top-3 predictions" in text
    assert "product-saas" in text
