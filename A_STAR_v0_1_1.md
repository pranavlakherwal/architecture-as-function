# A* v0.1.1 — Interim Release

**Status:** Interim. Frozen 2026-05-22. Supersedes v0.1 implementation notes; v0 spec (`A_STAR_v0.md`) unchanged.
**Why interim, not v0.2:** Wave 4 research (RQ9, RQ10, RQ12) is gated on Parallel.ai credit top-up. v0.2 spec close requires those findings. v0.1.1 captures everything we could ship without the wave.

---

## What landed in v0.1.1

### Implementation
1. **Stub-manifest generator** — `impl/tools/stub_manifest.py` + 10 unit tests.
2. **K-inference classifier** — `impl/tools/k_inference.py` + 14 unit tests. Worked impl for RQ11.
3. **Personal-twin worked application** — first non-Buuuk project run through the solver. Plan-only.

### Validation results
- **Buuuk:** 41 → 21 primitives after stub pass (-49%). UPDATE_MANIFEST: 37 → 17 (residual all inside `archive/`).
- **neural-gtm:** 30 → 1 primitive after stub pass (-97%). UPDATE_MANIFEST: 29 → 0.
- **Combined Layer A + Layer B:** 71 → 22 primitives. Plus 49 stubs that satisfy IC3 mechanically and flag human review via `lifecycle_status: bootstrap` + owner sentinel.
- **K-inference recall:** top-1 5/8 (0.625), top-3 6/8 (0.750) across 8 Neural projects. Misses are legitimately ambiguous (personal-twin lost research-memory vs intel-pipeline by 0.05 points, swamped by 13k HF leaderboard JSONs).
- **Personal-twin solver:** SAT, 5,313 primitives over 6,119 folders. Distribution: 5,236 UPDATE_MANIFEST / 73 ARCHIVE_FOLDER / 2 SCHEDULE_DESTRUCTION / 2 SET_SOURCE_OF_TRUTH.

## What v0.1.1 proved

1. **Stubs are enough to close IC3 mechanically.** A pre-filled `.manifest.yaml` with `lifecycle_status: bootstrap` + `owners: ["unknown (stub_manifest.py - review_required)"]` satisfies the schema and lets the solver focus on real architectural primitives instead of fire-hosing UPDATE_MANIFEST. This is the v0.1.1 unlock for any new K class.
2. **K is inferable, but structural features alone hit a 75% top-3 ceiling.** Need semantic tie-breaking (README/CLAUDE.md embedding) and per-K weight calibration.
3. **Personal-twin reveals v0.2 holes** (see below). The 5,313-primitive avalanche is a real signal: the solver's per-folder UPDATE_MANIFEST stamping doesn't scale, and `SCOPES` (currently hardcoded outbound-pipeline lexicon) misfires on research-memory.

## v0.2 candidate spec (driven by personal-twin findings)

1. **K-parametric SCOPES.** Today `SCOPES` is a constant lexicon (`lead_records, delivery_proof, etc.`). Needs to be K-indexed. Research-memory needs `project_context, capture_partial, identity_record, embedding_corpus, consent_record`.
2. **New primitive: `BULK_UPDATE_MANIFEST`** — single primitive that covers a subtree, to avoid 5k-primitive output.
3. **New primitive: `CONSOLIDATE_DUPLICATE`** — IC1 violations across `memory/projects/*` vs `memory/contexts/` need a primitive richer than `SET_SOURCE_OF_TRUTH`.
4. **New primitive: `LINK_INTEGRITY_SCAN`** — c_loss surrogate for memory-class K, where dead links are a primary decay mode.
5. **New axis candidate `c_privacy`** (RQ11b, see below). 7 → 8 axes for any K with sensitive data.
6. **PII heuristic tightening.** Substring match on `Contact`/`Doctor`/etc. false-fires on HF model names. Need lexeme-boundary or contextual signals.

## Open research

| RQ | Status | Blocker |
|---|---|---|
| RQ9 — K form (fixed vs lattice vs free) | thread spec written, queued in `protocols/wave4_threads.json` | Parallel.ai credit |
| RQ10 — Seam as primitive | queued in wave4 | Parallel.ai credit |
| RQ11 — Inverse classifier | **worked impl shipped v0.1.1**, recall report at `/tmp/k_inference_report_2026-05-22.md` | — |
| RQ11b — `c_privacy` axis | **NEW**, identified during personal-twin application | needs scoping |
| RQ12 — Seam cost | queued in wave4 | Parallel.ai credit |
| RQ13 — Folder decay measurement | skeletal RQ at `research/open/RQ13_folder_decay_measurement.md` | needs git-mining tool |

## Files in this release

- `impl/tools/stub_manifest.py`, `impl/tests/test_stub_manifest.py`
- `impl/tools/k_inference.py`, `impl/tests/test_k_inference.py`
- `research/v0_1_1_personal_twin_application.md`
- `protocols/wave4_threads.json` (ready, not launched)
- `/tmp/stub_manifest_report_2026-05-22.md`, `/tmp/k_inference_report_2026-05-22.md`

## What is **not** v0.1.1

- Wave 4 research outputs.
- Any change to the v0 spec (`A_STAR_v0.md`).
- Any mutation to personal-twin (plan-only as policy).
- The 17 residual Buuuk UPDATE_MANIFEST primitives inside `archive/` — policy call (tool skips `archive/`, solver does not).
