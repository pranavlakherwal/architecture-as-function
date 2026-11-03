# A* Research Roadmap

**Project:** Architecture as a Function. `A*(I, L, K, T) → (A, D)`
**Repo:** `/Core/Neural/PnotP/architecture-as-function/`
**Owner:** Pranav Lakherwal
**Last updated:** 2026-06-12

This is the single source of truth for A* research. All historical
docs (A_STAR_v0.md, A_STAR_v0_2.md, RQ memos) are reference. Status
and next actions live here.

---

## Current state

**Spec version:** v0.2 (closed 2026-05-22 at `A_STAR_v0_2.md`)
**Empirical phase:** Phase 3c complete (2026-05-25). **DIRECTIONAL.** (Downgraded 2026-06-06 from "PARTIALLY VALIDATED"; 4 of 5 stopping rules pass, but the headline modification law is ahead of its evidence. See "Related work and honest threats" below.)
**Headline equation result:** α = +8438, 95% CI [+4075, +12802], R² = 0.617. β = +0.209, R² = 0.871.
**Dataset:** 356 v2 rows across 8 ecosystems, 88 single-repo labels, Cohen's κ = 0.881.
**RQ12d Stage 1 (2026-06-10): α[engine] IS a throughput artifact.** On the consistent 1.0.2 population (5 ecosystems, N∈{1,10,50}), α[engine] ~ throughput(total_prs at N=1) gives **R²=0.9963, slope=7.61, CI [6.76, 8.46]**. The 63.3x per-ecosystem α spread (Phase 3c Rule 3) is not architectural signal; it re-encodes engine PR volume. Do NOT promote α[engine] as an independent constant into v0.3.
**RQ12d correction (2026-10-02, R.THRU.1): that R² is a sampling identity, not a throughput law.** The regressor is the length of the commit list the miner classified, and its `-n` cap cut that list short: linux 100 of the 16,221 commits in its window, vscode 1,500 of 7,075. Every tenant was classified against the same list, so α = sample size × rate per sampled commit, exactly, on all 5 engines. Against commits recounted from the clones with no cap, α ~ throughput gives **R²=0.018** (slope -0.10, p=0.83, n=5; the recount is a floor on postgres and WordPress). The 63.3x spread (vscode over linux) is 15.0x in sample size times 4.22x in rate. So the reason above (α re-encodes engine PR volume) does not stand. The action does: raw α is counted in a sample the cap set, so it is still not an architectural constant. Source: `impl/bench/results/rq12d_rq14_2026-10-01.{md,json}`.
**Classifier-era correction (2026-10-07, R.ERA.1): the headline α above pools rows counted by an older classifier.** The 216 per-tenant rows mined on 24 May (kubernetes, postgres, vscode, WordPress; two thirds of the 332) were counted before classifier 0.2.0 and never re-counted. Replayed from their own commit caches under 0.2.0, they hold fewer cross-cutting commits on every engine, from 1.2 times fewer (kubernetes, 55,553 to 45,202) to 3.4 times fewer (WordPress, 8,990 to 2,667). The 25 May rows replay to the stored numbers, 116 of 116. On the re-count, pooled **α = +4,989, 95% CI [+1,963, +8,015], R² = 0.540**: the sign holds and rules 1 and 2 still pass, but α is 41% smaller. The per-engine spread is 43.3x (kubernetes over linux), so rule 3 still fails. R.THRU.1's verdict holds (α ~ recounted throughput R² = 0.037), RQ14 is still undetermined (p = 1.04), and R.MACC.2's verdict holds (α ~ c_modify Spearman 0.43, PC still ahead raw and α still ahead holding throughput fixed). The store is unchanged; the re-count is in `impl/bench/results/classifier_era_2026-10-07.{md,json}`.
**Classifier version correction (2026-11-03, R.CLS.1): the classifier the code runs is 0.2.1, and the stamp now says so.** DL-241 (288ae69, 2026-10-18) let the H2 Go pattern match an import path that holds a dot and left `CLASSIFIER_VERSION` at 0.2.0, so for three weeks a row's stamp did not name the code that counted it. The version is now 0.2.1, each version is pinned to a hash of the classifier's logic (`impl/bench/mining/classifier_versions.json`), and a test fails when the logic moves and the version does not. All 332 per-tenant rows of both mining days were re-counted under 0.2.1 from their own caches, store untouched: 147 of 332 rows differ from 0.2.0, on 117 of 254 client repos, and every engine counts the same or more, from +0.0% (spring) to +17.2% (WordPress). Pooled **α under 0.2.1 = +5,077, 95% CI [+2,035, +8,118], R² = 0.546**, 1.8% above 0.2.0's +4,989; every verdict on this page reads the same under 0.2.0 and 0.2.1. The three eras a reader of α is choosing between (R.ERA.2): the store (+8,438, two classifiers, one of them unnamed), 0.2.0 (+4,989) and 0.2.1 (+5,077). Source: `impl/bench/results/classifier_era_2026-11-03.{md,json}`.
**RQ14 (2026-06-10): functional form UNDETERMINED.** Free-power refit gives **p=0.99, 95% CI [-1.64, 3.63]** (straddles 0.5 sqrt, 1.0 linear, 2.0 quad). AIC and BIC both prefer **linear** over sqrt/quadratic. The √N law was pinned, not chosen; at n=10 pooled points the exponent is not identifiable.

**RQ14 form correction (2026-11-02, R.FORM.1): the "linear" RQ14 leans to is the roll-up's construction, not a reading of the engines.** The observable RQ14 fits, delta_cc(N), is the SUM over the N client repos of each repo's cross-cutting count against one sampled commit list. Adding a repo adds its count, so over random subsets of a bucket's repos the sum's expected exponent is exactly 1.000 on all 5 engines. Replayed commit by commit from the rows' own caches (212 client repos, classifier 0.2.0 as of DL-241), a per-N observable that is not a sum, the UNION (sampled engine commits cross-cutting for at least one of the N repos), is already 53% to 100% of the sample at N=10 and 91% to 100% at N=50; its expected exponent is 0.09 to 0.19 (saturation, not growth). The spec's own c_modify(N) ("dependent updates" per change, A_STAR_v0.md) is the sum divided by the sample, so the spec's observable is a sum too; its growth is the per-repo rate times N, and a √N needs each added repo to be less coupled than the last, which buckets that add repos in name order cannot show. The spec's comment "cross-cutting touches all N" does not hold here: at N=50 a cross-cutting commit touches 10.8 to 29.0 of its repos, and at most 4.1% touch every repo. Source: `impl/bench/results/rq14_form_2026-11-02.md`.
**Next phase:** v0.3 spec close decision (lead with the storage law β; treat the modification law as throughput-confounded + form-undetermined).

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
| Phase 3c (RQ12c) | DIRECTIONAL | 2026-05-25 | α = +8438, R² = 0.617, 4/5 rules (form not yet chosen by data, see RQ14) |
| RQ12d Stage 1 | DONE, REASON CORRECTED 2026-10-02 | 2026-06-10 | α~store column R²=0.9963 is the sampling identity (α = sample × rate); α~recounted throughput **R²=0.018**. Raw α still not a constant (R.THRU.1) |
| RQ14 | DONE | 2026-06-10 | free-power p=0.99, CI [-1.64, 3.63]; AIC/BIC prefer linear; **form undetermined** |
| β battery (R.ABETA.1) | DONE | 2026-06-11 | **HARDENED**: jackknife 5/5 positive, bootstrap CIs [0.062,0.236]/[0.093,0.217] excl zero, 24-row ablation inert; caveat full-data n=10 fit 0.152 R²=0.58. First headless executor result. |
| v0.3 spec close | PENDING | TBD | do NOT absorb α[engine] as independent term (it's throughput-confounded) |

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
| RQ12d | Engine-throughput regressor | DONE Stage 1 2026-06-10, reason corrected 2026-10-02 | June R²=0.9963 is α = sample × rate by construction; on recounted throughput R²=0.018. Rule-3 spread is 15.0x miner sample size × 4.22x rate (R.THRU.1) |
| RQ13 | Folder decay rate | SKELETAL | unblocks c_drift confidence |
| RQ14 | Functional-form selection: free-power N^p vs linear vs quadratic (AIC/BIC) | DONE 2026-06-10 | p=0.99 CI [-1.64,3.63]; AIC/BIC prefer linear; **form undetermined at n=10** |

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

Spread: 63.3x. **RQ12d Stage 1 (2026-06-10) confirmed: α[engine] ~ throughput is R²=0.9963 — the spread is a throughput artifact, not architecture.** Corrected 2026-10-02 (R.THRU.1): the "throughput" column is the miner's capped sample (linux reads 100 here; its window holds 16,221 commits). The 63.3x is 15.0x sample size times 4.22x rate per sampled commit.

### Stopping rules (Phase 3c)
1. α CI excludes zero ✓ PASS
2. α R² ≥ 0.5 ✓ PASS (0.617)
3. per-eco spread ≤ 3x ✗ FAIL (63.3x, all signs positive)
4. classifier precision ≥ 0.85 ✓ PASS (1.000 on 45-PR gold)
5. Cohen's κ ≥ 0.7 ✓ PASS (0.881)

---

## RQ12d Stage 1 + RQ14 (2026-06-10)

Pure local compute on existing `measurements.db`. One command reproduces both:

```
/opt/anaconda3/bin/python3 impl/bench/fit_rq12d_rq14.py        # default --schema 1.0.2
```

**Schema filter (required):** `composite_measurements_v2` mixes `schema_version`
1.0.2 (277 rows, 5 ecosystems {kubernetes, linux, postgres, vscode, wordpress},
N∈{1,10,50}) and 1.0.3 (79 rows, 3 ecosystems {django, rails, spring},
N∈{1,10,15}) with **no stale column**. They differ in ecosystem set AND N-bucket
scale, so pooling mixes regimes. We fit the larger, wider-N **1.0.2** population.
(1.0.3 reruns reproduce the same qualitative story but cannot reach significance
at n=3 engines; reported in the JSON for honesty.)

### Correction (2026-10-02, R.THRU.1): the R² below is a sampling identity

The June fit below is reproduced exactly, and its reason does not hold.

- **What the regressor is.** `total_prs` at N=1 is the length of the commit
  list the miner classified (`git log -n<cap>`). The cap bound on linux (100
  of 16,221 commits in the window) and vscode (1,500 of 7,075).
- **Why it fits.** Every tenant in a bucket was classified against that one
  list, so a bucket's count is a sum of per-tenant counts. Checked on the
  store for all 5 engines. Hence α = sample size × rate per sampled commit,
  exactly, and regressing α on the sample measures only how flat the rate is.
- **The re-fit.** Against commits recounted from each clone with no cap:
  **R² = 0.018**, slope -0.10 (95% CI [-1.51, +1.31]), p = 0.83, Spearman
  -0.05, n = 5. The recount is a floor on postgres and WordPress (200-commit
  clones). The rate per sampled commit against the recount: R² = 0.37, p = 0.27.
- **The spread.** vscode over linux is 63.3x in α: 15.0x in sample size times
  4.22x in rate.
- **Verdict.** O.7's reason ("α re-encodes how many PRs each engine ships")
  does not stand. Its action stands: raw α is counted in a sample the cap
  set, so it is not an architectural constant and stays out of the
  Calibration Bus.
- **Not settled.** The rate is measured on the newest commits the cap let
  through, not a random sample of the window. Whether it moves with activity
  needs the counts re-mined on comparable samples.

Reproduce: `/opt/anaconda3/bin/python3 impl/bench/fit_rq12d_rq14.py`
(recounts from `impl/bench/workspace`). Artifacts:
`impl/bench/results/rq12d_rq14_2026-10-01.{md,json}` and the
`_schema1.0.3` pair.

### RQ12d Stage 1 — α[engine] is a throughput artifact (June reading, corrected above)

Regress per-engine count-form α (slope of `delta_cc ~ √N`) on engine baseline
throughput (`total_prs` at N=1), 5 engines:

| engine | α | throughput (total_prs N=1) |
|---|---|---|
| microsoft/vscode | 11254.6 | 1500 |
| kubernetes/kubernetes | 9516.8 | 1374 |
| WordPress/WordPress | 1276.6 | 200 |
| postgres/postgres | 809.7 | 200 |
| torvalds/linux | 177.8 | 100 |

- slope = **7.61** (95% CI [6.76, 8.46], excludes zero)
- **R² = 0.9963**, Pearson r = 0.9981, p = 0.0001
- **Verdict: α IS a throughput artifact.** Per-engine α is near-perfectly
  explained by how many PRs the engine ships. The Phase 3c Rule-3 spread
  (63.3x) is mundane: it re-encodes activity volume, not an architectural
  constant. **Do not promote α[engine] as an independent parameter into v0.3.**
  The downgrade to DIRECTIONAL (2026-06-06) is reinforced: the modification
  law's engine-to-engine variation is a throughput confound.

### RQ14 — functional form is undetermined (and leans linear, not √N)

Fit `delta_cc = a·N^p` (free power) vs linear (p=1) vs quadratic (p=2) on 10
pooled (engine, N>1) points:

| model | a | p | R² | AIC | BIC |
|---|---|---|---|---|---|
| free_power | 467.4 | 0.991 | 0.229 | 228.62 | 229.52 |
| linear (p=1) | 452.0 | 1.0 | 0.229 | **226.62** | **227.22** |
| quadratic (p=2) | 9.10 | 2.0 | 0.210 | 226.86 | 227.47 |

- free-power **p = 0.99, 95% CI [-1.64, 3.63]** (straddles 0.5 sqrt, 1.0 linear,
  2.0 quadratic)
- **AIC and BIC both prefer linear.** Free-power loses on the extra parameter
  without improving fit; the point estimate sits at ~1.0 (linear), not 0.5 (√N).
- **Verdict: functional form UNDETERMINED at n=10.** The √N shape was pinned, not
  chosen by the data. The honest report (per the 2026-06-06 look-back): the
  exponent is not identifiable here; pooled R²=0.23 because engines of vastly
  different throughput are mixed onto raw N without an engine factor. A
  per-engine-factor refit with more N-points is the path to identifiability.

**Downstream citation impact:** since α proves throughput-confounded and the √N
exponent is unsupported, any downstream text asserting "modification cost scales
as √(tenant count)" should be retracted to the look-back's honest claim:
"modification cost rises with tenant count and engine activity; the functional
form is not yet determined." Storage law (β) is unaffected and stands.

Artifacts: `impl/bench/fit_rq12d_rq14.py`,
`impl/bench/results/rq12d_rq14_2026-06-10.json`,
`impl/bench/results/rq12d_rq14_2026-06-10.md`.

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

## Related work and honest threats (added 2026-06-06, the look-back)

A foundations look-back against the field surfaced four things our own skepticism had not. Full citations in `BIBLIOGRAPHY.md` under "Foundational lineage and adversarial neighbors."

1. **A* is structurally Nam Suh's Axiomatic Design (1990), and we did not cite it.** Independence Axiom = our seam/IC3 and engine/tenant split; Information Axiom = our MDL prior. The honest reading: A* did not invent the framing. The defensible novelty narrows to "a calibrated cost model plus an SMT encoding." Claim that, not more.
2. **MacCormack's Design Structure Matrix propagation cost is a redundancy threat to the headline equation.** It already measures change-propagation-vs-coupling on real codebases with human-replicable metrics. Action: compute propagation cost on the 8 repos and test whether it predicts modification cost better than α·√N. If it does, the modification law is redundant, not just under-evidenced. This is the threat to lead with, not a footnote.
3. **The √N shape was pinned, not chosen.** A square root is the curve of economies of scale, the opposite of coordination cost (linear O(N), pairwise O(N^2), COCOMO exponent ~1.1). RQ14: re-fit as a free-power N^p, report p with a CI, use AIC/BIC against linear and quadratic. Let the data choose the exponent. If the CI straddles 0.5 and 1.0, the honest report is "functional form undetermined at n=2 per ecosystem."
4. **kappa=0.881 is consistency against a rubric, not agreement with humans.** Get a small human-labeled gold sample before claiming the labels are trustworthy.

What still holds and is ours: the **seam theorems** (Biba, Bell-LaPadula, Goguen-Meseguer non-interference, seL4) and the **storage law** (β=0.21, R²=0.871, the siloed multi-tenant cost form). Lead with those. The cleanest honest claim today: "Storage cost scales linearly per tenant. Modification cost rises with tenant count and engine activity; the functional form is not yet determined."

---

## Next steps (priority order)

### Now (this week)
1. ~~**RQ12d** Stage 1: engine-throughput regressor.~~ **DONE 2026-06-10, reason corrected 2026-10-02 (R.THRU.1):** the R² is α = sample × rate by construction, and on recounted throughput it is 0.018; see the correction above. June text: Result: α[engine] ~ throughput is R²=0.9963 → α is a throughput artifact, NOT an independent constant. Rule 3 will not be rescued by an α[engine] term; instead the throughput confound must be divided out *before* fitting the modification law (e.g. fit cross-cutting *fraction* per √N with a per-engine factor). Adding N=5/N=25 points is still the path to identifiability for RQ14.
2. ~~**RQ14** functional-form selection.~~ **DONE 2026-06-10, form corrected 2026-11-02 (R.FORM.1):** the sum's exponent is 1 by construction and the union saturates; see the correction above. More N-points per engine will not identify the exponent of a sum over name-ordered repos; the open question is whether the marginal repo's coupling falls with N, which needs repos ordered by when they adopted the engine. June text: Free-power p=0.99 CI [-1.64,3.63]; AIC/BIC prefer linear; form undetermined at n=10. Need more N-points per engine to identify the exponent.
3. **Finish Stream E cleanup** (30 min). Add `stale` columns, bump schema_version to 1.0.3.
4. ~~**MacCormack DSM propagation-cost test**~~ **DONE 2026-06-10, re-run at n = 8 on 2026-09-11 (R.MACC.2, commit 1081c7b), then with a real import resolver on every file on 2026-10-08 (R.MACC.4, commit df2b8e6).** The answer is directional, not powered (DL-146). From `impl/bench/results/maccormack_2026-10-08.{md,json}`, Spearman first: on raw ranks propagation cost (PC) tracks modification cost a little better than alpha (rho +0.333 vs +0.286). With engine throughput held fixed, alpha is ahead (partial +0.564 vs +0.071). Neither is significant: at n = 8 a partial needs |rho| of about 0.75 to clear p < 0.05, and every engine with an alpha is already in. PC is not collinear with alpha (rho +0.476), so the two measure different things. R.MACC.2 matched imports to files by path stems (raw +0.571 vs +0.286, partial +0.564 vs +0.087); the resolver replaces that. The June verdict below was n = 4-5, Pearson only, and recorded three engines as evicted that never were. It is superseded. June text: alpha ~ c_modify R^2 = 0.980 (p = 0.010); PC ~ c_modify R^2 = 0.054 (p = 0.768); PC not collinear with alpha (R^2 = 0.248). Artifacts: `impl/bench/results/maccormack_2026-06-10.{md,json}` (June), `impl/bench/results/maccormack_2026-09-10.{md,json}` (R.MACC.2), `impl/bench/results/maccormack_2026-10-08.{md,json}` (R.MACC.4), `impl/bench/maccormack_propagation.py`, `impl/bench/module_resolver.py`.

### Next (1-2 weeks)
3. **v0.3 spec close.** Leads with the β storage law + seam theorems. Records α as throughput-confounded with functional form undetermined (RQ12d + RQ14). Adds engine throughput to the I-vector as a CONFOUND control, not as a promoted constant. α[engine] is NOT folded in as an independent term.
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
