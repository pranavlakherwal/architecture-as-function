# A* v0 — Architecture as a Function

**Status:** P0P foundational research, v0 specification frozen 2026-05-21.
**Derived from:** Thinking pass (2026-05-21) + Wave 1 (RQ1, RQ2, RQ3) + Wave 2 (RQ4, RQ5, RQ6) + Wave 3 (RQ7, RQ8).
**Companion:** `BIBLIOGRAPHY.md` (annotated citations per RQ).

---

## 1. The Function

`A*` is a function from project context to architecture:

```
A*(I, L, K, T)  ->  (A, D)
```

where:

- `I` = intent (product goals, business goals, risk posture, novelty target, scenario suite)
- `L` = lifecycle stage (explore, bootstrap, production, scale, audit/archive)
- `K` = project class (one of 7 v0 constraint profiles)
- `T` = team vector (T_human, T_agent_internal, T_agent_external, T_onboard, T_reverse, T_devex)
- `A` = architecture state (folder structure, naming scheme, archival policy, manifests, source-of-truth registrations, persistence routing, graph relations)
- `D` = diagnostics (D_resilience, D_creativity, predicted C_core deltas, infeasibility evidence, rationale)

`A*` minimizes a 7-axis intrinsic cost vector `C_core` subject to 3 hard integrity constraints, conditional on `(I, L, K, T)`.

## 2. The Cost Vector `C_core`

Seven architecture-intrinsic axes (down from the original 9 — see §6 for the reduction):

| Axis | Meaning | Default measurement |
|---|---|---|
| `c_find` | Time to locate an artifact | Sinha 2023 search-task instrumentation; passive proxy = git/fs stats |
| `c_modify` | Time to apply a planned change including dependent updates | Code-churn + change-coupling (passive from git) |
| `c_storage` | Bytes on disk and cloud | Direct measure |
| `c_money` | Operating cost per unit time | Cloud bills + API spend |
| `c_drift` | Rate of integrity decay without intervention | Mannan structural entropy delta over time (HYBRID) |
| `c_loss` | Probability per unit time of misplacement, overwrite, orphan, dead link | FAIR v3.0-style annualized loss expectancy (HYBRID) |
| `c_derive` | Cost of regenerating derived views when source changes | INVENT: per-derivation cost model from cache invalidation literature |

**Predicted effective rank:** 3-4 (down from 4-5 in the original 9-axis vector). Confirmation requires the empirical study sketched in RQ1.

**Removed and reassigned:**

- `c_onboard` → split. Architecture-intrinsic learnability folds into existing axes (mainly `c_find` + `c_modify`); team/tooling capability moves to `T_onboard` (SPACE + DevEx evidence).
- `c_reverse` → split. Architecture irreversibility becomes a scenario diagnostic (`c_irreversibility_arch` in `D_resilience`); tooling/process capability moves to `T_reverse` (DORA + Git/Postgres/Statsig evidence).
- `c_blast` (failure containment) → optional 8th axis, included only for safety-critical, multi-tenant, or regulated K classes where blast radius has independent variance from `c_loss`, `c_drift`, and `c_reverse_arch`.

## 3. Hard Integrity Constraints

Three constraints. An architecture is invalid if any is violated.

**IC1 — Canonicality (single source of truth).** Every governed fact has exactly one source-of-truth artifact at a given scope, or an explicit derived/cache/exception status with a `derived_from` provenance edge.

**IC2 — Declared Retention and Verifiable Disposition** *(revised in RQ7, replacing the original "archival reversibility")*. Every artifact has a declared retention class `{active, archived, scheduled_for_destruction, destroyed}` and a destruction policy `{none, soft, hard, sanitize}` consistent with its artifact category, legal basis, retention schedule, and `K` class. Every destructive transition produces either:

1. a recoverable, integrity-checked archive when retention requires reversibility, OR
2. a verifiable destruction certificate plus residual record when retention requires irreversible deletion.

Soft delete is never terminal — it must resolve to archive or verified destruction by a declared deadline.

**IC3 — Manifest Consistency (folder-as-contract, revised in RQ5).** Every stable folder that functions as a navigation, ownership, lifecycle, or execution boundary declares a manifest containing: scope, exclusions, allowed artifact types, owner, lifecycle status, required metadata, outbound relations, and review cadence. For agent-heavy systems (`T_agent_internal` high), manifests must be machine-readable (YAML/JSON + JSON Schema) and CI-validated. Cross-cutting meaning lives in facets/tags; relation-dense meaning lives in typed graph edges. The repository ontology is layered across folders + facets + tags + graphs + schemas + search.

*The original sub-thesis "every folder is a small ontology" was weakened: PIM/IA literature does not support that universal claim. Folder = scoped contract; ontology = the larger layered scheme.*

## 4. Intent `I` — Goal-Shaping Parameters

`I` is no longer just product/business goals. Wave 2 added two explicit posture parameters:

**I_resilience** (from RQ6):
```
posture in {robust, rebound, graceful_extensible, antifragile}
SLOs, error budgets
scenario suite S_R
required recovery/containment bounds (MTTR, c_blast caps)
risk appetite alpha
```

**I_creativity** (from RQ6):
```
novelty_target in {low, medium, high, percentile}
exploration_budget
allowed_pattern_distance_from_K
analogy_domains
must_satisfy_quality_scenarios (ATAM)
unacceptable novelty risks
```

Resilience and creativity are NOT new cost axes. Resilience is a scenario constraint envelope plus posture. Creativity is intent + an output-side quality score `q_creativity = novelty × usefulness × fit` (Cross/Alexander/Shah-Smith-Vargas-Hernandez).

## 5. Project Class `K` — Seven Constraint Profiles

`K` is a constraint profile, not a domain label (RQ4 verdict). Each profile is:

```
K_profile = (H_K hard constraints, W_K ranked soft weights over C_core,
             T_K typical team composition, F_K failure-mode priors,
             E_K observability requirements)
```

The seven v0 classes, mapped to the Neural ecosystem seeds:

| K class | Hardest constraints | Top C axes | T composition | Seed |
|---|---|---|---|---|
| `outbound-pipeline` | fresh-leads-by-cutoff, deliverability-safe-send, idempotent sequence state | c_money > c_drift > c_modify | low T_human, high T_agent_internal/external | AgencyA |
| `content-pipeline` | source-provenance, audit-before-publish, publish-cutoff | c_derive > c_find > c_drift | med T_human, high T_agent_internal | LSD (primary) |
| `product-marketing` | catalog-truth, spend-ROAS-guardrails, attribution-window | c_money > c_drift > c_modify | med T_human, high T_agent_internal/external | BrandB |
| `product-saas` | RBAC-PII-isolation, schema-migration-safety, output-correctness | c_modify > c_loss > c_find | high T_human, med T_agent_* | UniversityC (LSD secondary) |
| `research-memory` | provenance + link-integrity, memory-isolation/consent, reversible/append-only updates | c_find > c_storage > c_derive | high T_human, high T_agent_internal | Personal Twin |
| `audit-pipeline` | immutable-source-retention, append-only audit log, reviewer-signoff | c_loss > c_find > c_derive | high T_human, high T_agent_internal | DeskD Engine |
| `intel-pipeline` | fresh-data-by-cutoff, source-timestamp-dedupe, distribution SLA | c_drift > c_find > c_derive | low/med T_human, high T_agent_internal/external | tenant-a-intel |

**Hybrids** (e.g., LSD = 0.65 content-pipeline + 0.35 product-saas): decompose into bounded contexts first (DDD), **union** hard constraints (never average), then blend soft weights. Never blend away a hard constraint.

**Lifecycle interaction:** `K` is stable by default; `L` modulates weights and activates constraints. Change `K` only if a new hard constraint binds for ≥2 review cycles or consumes >⅓ of architecture-change effort.

## 6. Team Vector `T` — Enriched in Wave 2

`T` now absorbs the capability dimensions that were confounding `c_onboard` and `c_reverse`:

```
T = {
  T_human, T_agent_internal, T_agent_external,        # composition
  T_onboard: {                                         # ramp-up capability
    documentation_quality, docs_freshness, setup_automation,
    code_search_quality, build_test_latency, mentor_capacity,
    review_latency, ownership_clarity, prior_skill_distribution
  },
  T_reverse: {                                         # rollback capability
    version_control_practice, CI_CD_maturity, feature_flag_coverage,
    DB_transaction_and_migration_tooling, backup_restore_capability,
    observability, runbook_quality, incident_response_maturity, SRE_maturity
  },
  T_devex: {                                           # SPACE/DevEx
    SPACE_dimensions, feedback_loop_latency, cognitive_load_sources,
    flow_interruptions, collaboration_practices
  }
}
```

This lets `A*` condition recommendations on the team's actual capability. A team with weak rollback tooling receives architectures that minimize irreversible changes; a team with mature flags + observability can safely use progressive-delivery patterns.

## 7. Functional Form — Hybrid COP via Z3 Optimize

**v0 winner (RQ2):** Hybrid Constraint Optimization Problem (COP) solved with Z3 Optimize. Hard integrity constraints via `assert`; soft objectives via `assert-soft` with weights from `W_K`. Multi-objective handling via Z3's lexicographic, Pareto, or box modes — not collapsed to a scalar unless degrees of freedom are fixed.

**Why this wins:**
- Hard constraints are first-class (won't be silently relaxed for cost gain).
- Multi-objective trade-offs are explicit, not hidden in weighting.
- Interpretable: Z3 emits a model with named variables; unsat returns a core.
- Incrementally tunable (push/pop, add constraints without re-derivation).
- Mature tooling for our problem size (5-200 architectural primitives).

**v1 evolution path:** FastSMT for ~100× speedup; neuro-symbolic learned heuristics over the constraint search; learned `W_K` calibration from observed cost deltas.

**Honest gap:** No prior published work applies COP end-to-end to folder/naming/persistence/archival decisions. A* is novel synthesis.

## 8. `S(M,T)` as the Routing Special Case of A*

**Formal reduction (RQ8):** S(M,T) — the routing simplicity-times-fit scalar from earlier P0P work — is A* with the architecture search space restricted to model selection.

```
S(M, T) = [Π_j gate_j(M, T)] · [Σ_i w_i · φ_i(M, T)] · exp(-β · H_i)
```

reduces from:

```
A*(I, L, K, T)
   when K = routing
   AND folder_structure, naming_scheme, archival_policy, persistence_layer are fixed
   AND only free variable is model/route M
```

Substitutions:

| S(M,T) term | A* term |
|---|---|
| `gate_j(M,T)` | `G_j(A_M, x)` hard integrity constraint |
| `Π_j gate_j` | feasibility filter |
| `φ_i(M,T)` | `norm_i(-c_i(A_M, x))` negative cost utility |
| `w_i` | `W_K[i]` profile-calibrated soft weight |
| `H_i` | `H_simp(A_M, x)` complexity regularizer |
| `β` | regularization strength, varies with `K`, `L` |

Therefore `argmax_M S(M, T) = A*(I, L, K=routing, T)`.

**Reverse import:** A* should adopt an explicit simplicity prior `H_simp` (MDL, Solomonoff, AIC/BIC, Parnas information hiding). Placement: soft objective in `C_core` + Pareto tie-breaker among non-dominated candidates. NOT a hard constraint (audit trails, manifests, lineage edges are necessary complexity).

**Where the reduction fails (A* generalizes strictly beyond S):**
1. Discrete structural outputs (vs scalar scoring)
2. Multi-objective trade-offs (Z3 Pareto vs single scalar)
3. Hard constraints with side effects (archival reversibility requires emitted operations, not just a gate)
4. Lifecycle modulation (L changes both constraints and weights)
5. Team-vector enrichment (same A has different `T_onboard` cost for different teams)

## 9. Primitive Operations — What A* Emits

A* does not emit a final state. It emits **target state + primitive transaction + diagnostics**. (RQ8 + migration-tool convergence: Alembic/Django/Prisma/Liquibase/Flyway all use versioned upgrade/downgrade.)

**Minimal complete primitive set (9 ops, reduced from 17 candidates):**

1. `CREATE_FOLDER` — addressable container with purpose, owner, manifest_ref
2. `ARCHIVE_FOLDER` — move to archive namespace with retention policy
3. `MOVE_ARTIFACT` — relocate (subsumes RENAME via path delta)
4. `DUPLICATE_TO_CACHE` — non-canonical derived copy with `derived_from`, TTL, invalidator
5. `SET_SOURCE_OF_TRUTH` — register/promote/retire canonical authority for a scope
6. `UPDATE_MANIFEST` — patch manifest with schema validation + inverse_patch
7. `UPSERT_RELATION` — add/update/remove tag, facet, lineage edge, graph relation
8. `MIGRATE_PERSISTENCE` — change backend (fs ↔ DB ↔ object store ↔ vector ↔ index)
9. `SCHEDULE_DESTRUCTION` — deletion behind retention + approval gate, never immediate

Macros (`SPLIT_FOLDER`, `MERGE_FOLDERS`, `PROMOTE_DERIVED_TO_SOURCE`, etc.) compile to sequences of these 9.

**Each primitive declares:** inputs, effect, pre-conditions, post-conditions, per-axis `C_core` delta, reversibility status, which integrity constraints can be violated by misuse, typical K-class use.

**Composition:** A* emits a transaction (DAG of primitives) with atomic-commit semantics and an inverse plan. Topologically sorted. Each operation has an inverse (or explicit `irreversible: true` + waiver).

**Operator-facing emission format:** YAML/JSON with `target_architecture`, `primitive_plan`, `expected_C_core_delta`, `constraints_validated`, `diagnostics` (D_resilience, D_creativity, infeasibility), and human-readable `rationale`.

## 10. Per-K-Class Archival Policy (Excerpt)

From RQ7. Defaults; overridden by jurisdiction, contract, legal hold.

| K class | Must irreversibly destroy | Must archive | Typical windows | Storage tier |
|---|---|---|---|---|
| outbound-pipeline | expired contact PII beyond suppression, credentials | consent receipts, suppression records, delivery proofs | raw 30-90d; consent 3-7y | hot+warm+cold/WORM |
| content-pipeline | prompt logs with PII post-review, temp renders, embedded secrets | published assets, rights, approvals, source versions | temp 7-30d; rights for contract+dispute | hot+warm/cold; WORM if regulated |
| product-marketing | raw events after aggregation, expired leads | consent, campaign attribution, experiment decisions | raw 30-180d; aggregates 13-25mo; consent 3-7y | hot+warm+cold |
| product-saas | deleted-account PII post-grace, secrets, PCI excess, raw debug logs | ledgers, invoices, audit trails, versioned configs | account grace 7-30d; backups 30-90d; financial 7y | hot DB+warm logs+cold backups+WORM audit |
| research-memory | raw PII without consent, sensitive prompts, embeddings retaining sensitive source | dataset cards, consent/provenance, reproducibility manifests | sensitive: project+30-90d; manifests 3-7y | hot+warm feature store+restricted WORM |
| audit-pipeline | convenience copies after authoritative archive + retention expiry | audit logs, workpapers, access logs, chain-of-custody | 7y under SEC-style rules; destruction only post-hold-release | WORM-first |
| intel-pipeline | live credentials, raw scraped PII without basis, obsolete high-risk indicators | source provenance, analytic reports, chain-of-custody, sanitized indicators | raw 30-180d; reports 1-7y; secrets immediate rotation | hot secure enclave + warm graph + cold/WORM chain-of-custody |

## 11. Closing Gaps (RQ8, flagged for v1)

The v0 spec is frozen. The following gaps are explicitly deferred:

| Gap | v1 recommendation |
|---|---|
| Incremental tuning vs full re-derivation | Incremental when no hard constraint changes and delta cost < churn threshold; full re-derivation for source-of-truth, persistence, or integrity changes |
| Operator overrides | Soft-objective override: reason + approver + expiry; hard-constraint override requires waiver + rollback plan |
| Observed-cost learning | Log predicted vs observed `C_core` deltas + rollback events; recalibrate `W_K`, `T`, `β` |
| A* self-versioning | Every run records `spec_version`, solver version, primitive schema version, `C_core` schema version, `K` profile version, manifest schema version |
| Infeasibility diagnostics | On unsat: return failed constraints, relaxations, minimum waiver set, remediation options |
| Permission model | Dry-run + capability manifest + approval gates; separate permissions for migration, canonicality, destruction |
| `C_core` measurement | Per axis: unit, range, normalization, source, confidence, owner, update cadence |
| Macro expansion audit | Render macros for humans; validate and execute compiled primitive plan |

## 12. v0 → v1 Roadmap

**v0 (this document):**
- Definition, schema, integrity constraints, K taxonomy, primitive operations all frozen.
- Solver = Z3 Optimize hybrid COP.
- Single test repo = AgencyA (outbound-pipeline).

**v0.1 (next 4 weeks):**
- Implement `H_K`, `W_K`, `T_K`, `F_K` as static dictionaries for the 7 K classes.
- Build manifest schema + CI validator.
- Z3 model for AgencyA transformation; emit YAML primitive plan.
- Passive `C_core` measurement instrument (7 axes from git/fs/CI).

**v0.2 (8-12 weeks):**
- Apply to LSD (content-pipeline + product-saas hybrid) and Personal Twin (research-memory).
- Run K verification protocol (constraint extraction test, blind assignment, COP prediction, scenario stress, lifecycle stability, hybrid decomposition, observed-cost test).
- Calibrate `W_K` from observed deltas.

**v1 (3-6 months):**
- All 7 seed projects under A* governance.
- Empirical rank study of `C_core` across 5-10 repos (RQ1 next-experiment design).
- FastSMT prototype.
- Operator override + observed-cost learning loops shipped.

## 13. Honest Limitations

- **No empirical validation yet.** Effective rank, K class predictiveness, primitive completeness — all are arguments from literature + reasoning, not measurement.
- **No prior end-to-end COP for folder/naming/persistence architecture exists** (RQ2 honest gap). A* is genuinely novel synthesis.
- **`c_derive` measurement is INVENT-tier.** No existing literature gives a defensible procedure.
- **Decay rate for folder hierarchies is unknown** (RQ5). The literature documents failure modes but no universal "X% per year" constant. Local measurement required.
- **Agent-vs-human cost weighting is asserted, not validated.** Wave 1 thinking pass claimed `T_agent_internal` dominates; needs empirical confirmation.
- **The 7-class K taxonomy is bootstrap.** Verification protocol may merge or split classes after observing 5-10 unseen projects.

## 14. References

See `BIBLIOGRAPHY.md` for full annotated citations organized by RQ. Key anchors:

- **COP / Z3:** de Moura & Bjørner; Bjørner, Phan, Fleckenstein (νZ); Z3 Optimize documentation
- **Cost dimensions:** DORA + SPACE + DevEx (Forsgren, Storey, Noda); COCOMO II (Boehm); FAIR v3.0
- **Constraint engineering:** ATAM (Bass/Clements/Kazman/Klein); DDD (Evans, Vernon, Fowler)
- **Knowledge organization:** Rosenfeld + Morville; PARA (Forte); Zettelkasten (Ahrens); Diataxis (Procida); Bergman et al.; Whittaker et al.; Voit TagTrees
- **Resilience:** Hollnagel RAG; Woods graceful extensibility; Cook; Taleb; Google SRE; chaos engineering
- **Creativity:** Cross; Alexander (*Notes*, *Pattern Language*); Shah/Smith/Vargas-Hernandez novelty+usefulness
- **Retention/disposition:** GDPR Art. 17; CCPA/CPRA; PCI DSS v4.0.1; 17 CFR 210.2-06; NIST SP 800-88 Rev. 2; ISO 15489; MoReq2010; OAIS/PREMIS
- **Engineering patterns:** Kafka log compaction; CRDT tombstones; Restic; ZFS/S3 Object Lock; Alembic/Django/Prisma/Liquibase/Flyway migrations
- **Simplicity prior:** MDL (Rissanen); Solomonoff; Burnham + Anderson (AIC/BIC); Parnas information hiding

---

*A* v0 is the foundation, not the destination. Ship v0, instrument AgencyA, learn, ship v1.*
