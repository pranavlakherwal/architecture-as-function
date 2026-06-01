# A* Research Roadmap

**Project:** Architecture as a Function. `A*(I, L, K, T) → (A, D)`
**Repo:** `/Core/Neural/PnotP/architecture-as-function/`
**Owner:** Pranav Lakherwal
**Last updated:** 2026-05-25

This is the single source of truth for A* research. All historical
docs (A_STAR_v0.md, A_STAR_v0_2.md, RQ memos) are reference. Status
and next actions live here.

---

## Current state

**Spec version:** v0.2 (closed 2026-05-22 at `A_STAR_v0_2.md`)
**Empirical phase:** Phase 3c complete (2026-05-25). **PARTIALLY VALIDATED.** 4 of 5 stopping rules pass.
**Headline equation result:** α = +8438, 95% CI [+4075, +12802], R² = 0.617. β = +0.209, R² = 0.871.
**Dataset:** 356 v2 rows across 8 ecosystems, 88 single-repo labels, Cohen's κ = 0.881.
**Next phase:** RQ12d (engine-throughput regressor) + v0.3 spec close decision.

---

## Phase tracker

| Phase | Status | Date | Key output |
|---|---|---|---|
| v0 spec | DONE | 2026-05-21 | A_STAR_v0.md (8 RQs across 3 waves, ~$5 Parallel.ai) |
| v0.1 AgencyA impl | DONE | 2026-05-21 | 111 → 71 primitives, Z3 solver shipped |
| v0.1.1 personal-twin | DONE | 2026-05-22 | 5,313 primitives, exposed v0.2 holes |
| Wave 4 (RQ9/10/12) | DONE | 2026-05-22 | 168KB, Claude Code native, $0 spend |
| v0.2 spec close | DONE | 2026-05-22 | A_STAR_v0_2.md (K lattice, IC3+asymmetric, conditional split) |
| Phase 1 bench | DONE | 2026-05-22 | 5 golden fixtures, 40 rows, 5 gates green |
| Phase 2 bench | DONE | 2026-05-22 | 88 labels, Cohen's κ = 0.881 |
| Phase 3a (option a) | FALSIFIED | 2026-05-22 | α = -1.57 (wrong observable) |
| Phase 3b (option b) | PARTIAL | 2026-05-24 | α = +3746, R² = 0.25, sign correct |
| Phase 3c (RQ12c) | PARTIAL | 2026-05-25 | α = +8438, R² = 0.617, 4/5 rules pass |
| RQ12d | PENDING | TBD | engine-throughput regressor → VALIDATED target |
| v0.3 spec close | PENDING | TBD | absorb α[engine] term |

---

## Research questions tracker

| RQ | Topic | Status | Output |
|---|---|---|---|
| RQ1 | C_core axes (7 vs 9) | DONE wave 1 | reduced to 7, c_onboard/c_reverse → T |
| RQ2 | Integrity constraints | DONE wave 1 | IC1/IC2/IC3 |
| RQ3 | K class taxonomy | DONE wave 2 | 7 bootstrap classes |
| RQ4 | I vector enrichment | DONE wave 2 | I_resilience + I_creativity added |
| RQ5 | Folder-as-contract vs ontology | DONE wave 2 | weakened to folder-as-contract |
| RQ6 | T enrichment | DONE wave 2 | T_human/T_agent_internal/T_agent_external + 3 more |
| RQ7 | IC2 retention semantics | DONE wave 3 | rewritten as declared retention + verifiable disposition |
| RQ8 | S(M,T) reduction proof | DONE wave 3 | formal reduction of S(M,T) to A* with K=routing |
| RQ9 | K form (fixed / lattice / free) | DONE wave 4 | lattice with 4 operators, depth ≤ 3 |
| RQ10 | Seam as primitive | DONE wave 4 | fold into IC3 as asymmetric-flow theorems |
| RQ11 | K inference classifier | DONE v0.1.1 | top-1 5/8, top-3 6/8 on 8 Neural projects |
| RQ11b | c_privacy 8th axis | CANDIDATE | not promoted yet, needs scoping |
| RQ12 | Seam cost (two-layer split) | DONE wave 4 | conditional default under R1∨R2∨R3 |
| RQ12b | PR-mining engine (option b) | DONE Phase 3b | α flipped sign to positive |
| RQ12c | Classifier + heterogeneity + width | DONE Phase 3c | R² 0.25 → 0.617, 4/5 rules |
| RQ12d | Engine-throughput regressor | OPEN | target VALIDATED (5/5) |
| RQ13 | Folder decay rate | SKELETAL | unblocks c_drift confidence |

---

## What we have built

### Spec layer
- `A_STAR_v0.md` (frozen, the formal synthesis)
- `A_STAR_v0_1_1.md` (interim, personal-twin findings)
- `A_STAR_v0_2.md` (closed, K lattice + seam + conditional split)
- `BIBLIOGRAPHY.md` (annotated, per-RQ)
- `thinking/a_star_thinking_v1_20260521.md`

### Implementation layer (`impl/a_star/`)
- `profiles/k_profiles.py` — 7 frozen K profiles + H_K/W_K/T_K/F_K/E_K registries
- `manifest/{schema,validator}.py` — JSON Schema Draft 2020-12, IC2+IC3 unified
- `measurement/core_vector.py` — 7-axis passive measurement, runner v0.2.1
- `solver/{introspect,model,plan,cli}.py` — Z3 Optimize hybrid COP
- `tools/stub_manifest.py` — IC3 mechanical closer (AgencyA 41 → 21 primitives)
- `tools/k_inference.py` — RQ11 worked impl

### Empirical layer (`impl/bench/`)
- 11 Python modules: collect, measure, fit, card, cli, storage, schema, quality
- `mining/`: github_pr_miner, local_git_miner, cross_cutting (v0.2.0 with H1+H2+H3 AST), composite_v2, ast_imports, heterogeneity
- 7 quality gates: schema, provenance, determinism, golden, outliers, pr_mining_reproducibility, classifier_precision
- 5 golden fixtures: sqlite, redis, WordPress, NASA F Prime, torvalds/linux
- 88 labels across 7 K classes, 30 blind-sample relabels (κ = 0.881)
- 356 v2 PR-mining rows across 8 ecosystems
- 45-PR gold set at `gold/cross_cutting_gold_v1.yaml` (agent-labeled)
- Schemas locked at JSON Schema Draft 2020-12, runner_version log in CHANGELOG

### Research artifacts
- `research/wave{1,2,3}/RQ*.md` — 8 deep-research memos (Parallel.ai)
- `research/wave4/RQ{9,10,12}-*.md` — 3 deep-research memos (Claude Code native, 168KB)
- `research/v0_1_1_personal_twin_application.md`
- `research/open/RQ13_folder_decay_measurement.md` — skeletal
- `protocols/wave{1,2,3,4}_threads.json` — audit trail
- `protocols/launch_wave.py` — reusable Parallel.ai launcher

### Results
- `impl/bench/results/PHASE3B_VERDICT.md` — Phase 3b verdict
- `impl/bench/results/PHASE3C_VERDICT.md` — Phase 3c verdict (current)
- `impl/bench/results/fit_2026-05-25_v3.json` — current fit numbers
- `impl/bench/results/EQUATION_REVISION_NEEDED.md` — Phase 3b → 3c rationale
- `impl/bench/card.md` — dataset card (Gebru et al format)

---

## Key empirical numbers (Phase 3c)

### Cost equation
```
C(place, K) = Σᵢ W_K[i] · normᵢ(cᵢ(place))         # per-K cost
c_modify(N)  ≈ c_modify(1) + α · √N                 # α calibrated
c_storage(N) ≈ c_storage(1) · (1 + (N−1) · β)       # β calibrated
c_drift(N)   ≈ c_drift(1) / N                       # not yet calibrated
c_loss(N)    ≈ c_loss(1) / N                        # not yet calibrated
```

### Calibrated parameters
| Parameter | Value | 95% CI | R² | Status |
|---|---|---|---|---|
| α (count form) | +8438 | [+4075, +12802] | 0.617 | 4/5 rules pass |
| β | +0.209 | [+0.129, +0.290] | 0.871 | healthy, all rules pass |

### Per-ecosystem α
| Ecosystem | α | Notes |
|---|---|---|
| kubernetes | +9517 | high throughput (13740 PRs/90d) |
| vscode | +11255 | high throughput |
| wordpress | +1277 | mid |
| django | +1596 | mid |
| spring | +922 | mid |
| postgres | +810 | low throughput |
| rails | +559 | low |
| linux | +178 | lowest throughput (100 PRs/90d) |

Spread: 63.3x. Tracks engine PR-throughput linearly. RQ12d will test α[engine] ∝ throughput.

### Stopping rules (Phase 3c)
1. α CI excludes zero ✓ PASS
2. α R² ≥ 0.5 ✓ PASS (0.617)
3. per-eco spread ≤ 3x ✗ FAIL (63.3x, all signs positive)
4. classifier precision ≥ 0.85 ✓ PASS (1.000 on 45-PR gold)
5. Cohen's κ ≥ 0.7 ✓ PASS (0.881)

---

## Honest limits (as of 2026-05-25)

- **Gold is agent-labeled, not human.** Classifier precision = 1.0 is internal consistency vs deterministic rubric.
- **No GITHUB_TOKEN.** All 356 v2 rows are `data_source='local_git'`.
- **2 N-points per engine.** Per-ecosystem R² = 1.0 is mechanical from n=2, not predictive.
- **24 aggregate-baseline rows kept.** Not marked stale (load-bearing for count-form fit).
- **c_drift, c_loss, c_money still uncalibrated.** β calibrated; α calibrated to 4/5; others on TODO.
- **Stream E partial.** `stale` columns not added, schema_version still 1.0.2 (only runner_version log bumped to 0.4.0).
- **No third-party replication.** Solo research, no peer review yet.

---

## Next steps (priority order)

### Now (this week)
1. **RQ12d** (1-2 agent days). Add engine-throughput regressor: α[engine] ∝ throughput[engine]. Add N=5 and N=25 points. Test logit transform on fraction form. Target: 5/5 stopping rules → VALIDATED.
2. **Finish Stream E cleanup** (30 min). Add `stale` columns, bump schema_version to 1.0.3.

### Next (1-2 weeks)
3. **v0.3 spec close.** Fold α[engine] into A_STAR_v0_3.md. Adds throughput as fifth I-vector field.
4. **v1 AgencyA re-run.** Re-run v0.1 AgencyA transformation with v0.2 spec + calibrated weights. First feedback loop from empirical → architectural decision.

### Later (when ready)
5. **RQ11b.** c_privacy as 8th axis (was tabled; revisit after VALIDATED).
6. **RQ13.** Folder decay measurement. Unblocks c_drift confidence promotion.
7. **External replication.** Pre-print? Submission to ICSE / FSE / EASE empirical software track?
8. **GITHUB_TOKEN integration.** Replace local_git with GitHub REST for cross-validation.
9. **Public release.** Bench corpus → HuggingFace, code → public GitHub.

---

## How to resume work

If returning cold to this project:

1. Read this file.
2. Read `impl/bench/results/PHASE3C_VERDICT.md` for latest empirical state.
3. Read `A_STAR_v0_2.md` §1 (equation) and §4 (scaling laws) for spec.
4. Check `impl/bench/measurements.db` `composite_measurements_v2` table for current data.
5. Bench-agent CLI: `/opt/anaconda3/bin/python3 -m bench.cli --help` from `impl/`.
6. To dispatch RQ12d, follow the same pattern as `RQ12C_PLAN.md` but with the engine-throughput regressor scope.

---

## Cross-references

- Master research roadmap: `/Core/Neural/RESEARCH_ROADMAP.md`
- Neural Scholar agent (for ongoing research execution): `/Core/Neural/agents/neural-scholar/`
- Personal-twin embeddings + graph for this research live in Qdrant collection `research_milestones` and Neo4j label `:ResearchMilestone`.
