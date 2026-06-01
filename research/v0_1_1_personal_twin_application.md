# A* v0.1.1 application: personal-twin (plan-only)

Date: 2026-05-24. Mode: read-only. Repo: `/Users/pranavlakherwal/Core/Neural/personal-twin/`.
Spec: A_STAR_v0.md frozen 2026-05-21. Solver: `impl/a_star/solver/`. K profile: `research-memory`.

## 1. K-inference top-3

```
intel-pipeline      score=53.45  conf=0.22
research-memory     score=53.40  conf=0.22
audit-pipeline      score=49.38  conf=0.20
```

Classifier inputs: 15,549 files, 84.4% `.json` (13,127), 4.1% `.py` (635), 409 markdown. Presence flags ON: `memory_dir, creatives_dir, audit_dir, tests, frontend, schemas, agents, prompts, manifests`. Filename hits: `memory_kw=74, audit_kw=80, intel_kw=51`.

The `.json` dominance comes almost entirely from `data/raw/open_llm_leaderboard/` (HuggingFace metadata dump, not memory). Stripped of that artifact, the top-1 should flip cleanly to `research-memory`. The classifier was right to refuse confidence (0.22). **Fix for v0.2: weight by directory diversity, not raw extension count, or treat `data/raw/` as a sink that doesn't contribute to K signal.**

## 2. Solver result

`solver_status = sat`, **5,313 primitives over 6,119 folders.**

| op | count |
|---|---|
| UPDATE_MANIFEST | 5,236 |
| ARCHIVE_FOLDER | 73 |
| SCHEDULE_DESTRUCTION | 2 |
| SET_SOURCE_OF_TRUTH | 2 |

Top by cost-reduction signal:
1. SCHEDULE_DESTRUCTION `<root>` (IC2 secret-at-rest, +30d sanitize, approval required)
2. SCHEDULE_DESTRUCTION `memory/projects/trishaan-claude-code-mastery/si-global-intel` (same)
3. SET_SOURCE_OF_TRUTH `data/raw/open_llm_leaderboard` for scope `lead_records` (**FALSE POSITIVE**: HF leaderboard ≠ leads)
4. SET_SOURCE_OF_TRUTH `data/raw/open_llm_leaderboard/SentientAGI` for `delivery_proof` (**FALSE POSITIVE**)
5-77. ARCHIVE_FOLDER on `data/qdrant/collections/build_improvements_auto_search` and 72 HF-leaderboard model dirs (clearly stale derived data, correct)
78+. 5,236 UPDATE_MANIFEST calls, every folder missing `.manifest.yaml`

## 3. Stub-manifest dry-run

`would_write = 6,068`, `skipped = 45` (folders that already carry a manifest). Apply = false.

For comparison: Buuuk plan = 111 primitives over 110 folders. Personal-twin is ~48× larger by folder count and ~48× larger by primitive count. Density (primitives/folder) is nearly identical (0.87 vs 1.01), which is itself a sign the solver isn't generating shape-aware recommendations, just per-folder UPDATE_MANIFEST stamps.

## 4. IC violations

- **IC1 canonicality**: 2 SET_SOURCE_OF_TRUTH primitives, both wrong (matched on filename hints for `lead_records` / `delivery_proof` against a HuggingFace model dump). True IC1 work for personal-twin would be: duplicate context across `memory/projects/*` and `memory/contexts/`, duplicate identity files (`identity.json`, `people.json`, `patterns.json` exist both at root and inside projects). The solver did NOT detect this because IC1 scopes are still bootstrap-outbound-pipeline (`SCOPES` in `introspect.py` lines 76-90).
- **IC2 retention**: 10 hits. Real positives include `memory/prospects` (PII), `<root>` (secret-at-rest from `.env`-style files), and `memory/projects/trishaan-claude-code-mastery/si-global-intel` (nested credential surface). False positives: HF `data/raw/open_llm_leaderboard/*` flagged as "contact" PII because of substring match on "Contact" in repo names.
- **IC3 manifest**: 2,145 stable-boundary violations (folders ≥ `min_stable_files=3` with no manifest). This is the dominant signal and it's correct. Personal-twin has near-zero `.manifest.yaml` coverage.

## 5. Buuuk vs personal-twin axis profile

| K-class | primary | secondary | tertiary | binding |
|---|---|---|---|---|
| outbound-pipeline (Buuuk) | c_money (0.30) | c_drift (0.22) | c_modify (0.16) | c_money (sender reputation) |
| research-memory (PT) | c_find (0.30) | c_storage (0.22) | c_derive (0.16) | should be c_drift + c_loss |

The W_K weights for research-memory are written as `c_find > c_storage > c_derive`, which assumes the binding constraint is retrieval quality and storage cost. On the real repo, `c_storage` IS dominant (6,119 folders, HF dumps), but the *real* failure mode visible in the plan is `c_drift` (provenance rot, dead links across moved folders, identity-file duplication). The current weighting under-counts that.

c_find dominates Z3 nowhere visible in the plan, because the solver has no "fragmented retrieval surface" primitive yet — no way to express SPLIT or MERGE or CANONICALIZE_LINKS.

## 6. Verdict: v0.1 transfers partially. v0.2 changes needed:

1. **K-specific SCOPES table.** `SCOPES` is hardcoded outbound-pipeline. Research-memory needs `{project_context, capture_partial, identity_record, embedding_corpus, consent_record}`. Without this, IC1 produces nonsense like "HF leaderboard is canonical for lead_records."
2. **Volume-aware primitive emission.** 5,236 UPDATE_MANIFEST calls is not a plan, it's a fire-hose. Group by parent folder, emit one `BULK_UPDATE_MANIFEST` per stable boundary with a glob.
3. **New primitive: `CONSOLIDATE_DUPLICATE`.** Personal-twin has `identity.json` at root and inside multiple projects. SET_SOURCE_OF_TRUTH alone can't express "pick one, redirect others to symlink-or-import."
4. **New primitive: `LINK_INTEGRITY_SCAN`.** F_K research-memory lists `dead_links_after_source_move` as a top failure prior but no primitive addresses it.
5. **PII heuristic refinement.** The `_PII_HINTS` substring match (`contact`, `lead`) fires on `ContactDoctor` HF model names. Either tighten to filename-only (not folder-only) or add an exclude list for `data/raw/`.
6. **K-class axis weight calibration.** For research-memory v0.2, rebalance to `c_find=0.26, c_drift=0.22, c_storage=0.18, c_loss=0.16, c_derive=0.10, c_money=0.04, c_modify=0.04`. Drift and loss are the real binding constraints on a personal memory store, not storage cost.

## 7. New RQ candidate

**RQ11b: privacy-class axis for K = research-memory.** The 7-axis C_core has no axis for "exposure cost" or "consent violation cost." For personal-twin (and any K with sensitive PII), an 8th axis `c_privacy` = expected cost of unintended disclosure × probability per primitive would alter the cost surface materially. SCHEDULE_DESTRUCTION on `<root>` would weight higher than ARCHIVE_FOLDER on stale HF dumps even though both are flagged. v0.1 conflates them under `c_money + c_drift`. Worth a deep-research pass before v0.2 freezes axis count.

## 8. Limitations of this run

- Plan-only. Nothing in personal-twin was modified.
- 5,236 UPDATE_MANIFEST primitives are noise more than signal; the real lesson is "stub-manifest generator should run first as a pre-pass, then A* solves over the reduced surface."
- The 2 SCHEDULE_DESTRUCTION targets need human review before any apply. `<root>` flag is from `.env` detection; real action is rotation, not destruction.
- IC1 false positives mean SET_SOURCE_OF_TRUTH output is not actionable until SCOPES is K-parametrized.

Word count: ~795.
