# A* v0.2 — Spec Close

**Status:** Spec close, frozen 2026-05-22. Supersedes the v0.1.1 interim note. The v0 spec (`A_STAR_v0.md`) remains the foundational document; v0.2 is a structured diff against it, derived from Wave 4 deep research (RQ9, RQ10, RQ12) plus the v0.1.1 personal-twin worked application.

**Wave 4 path:** Pivoted from Parallel.ai (HTTP 402 credit blocker) to Claude Code native deep search. Three parallel agents, WebSearch + WebFetch driven. Total output: ~168 KB across three citation-backed memos at `research/wave4/{RQ9, RQ10, RQ12}.md`. No Anthropic API, no Parallel.ai spend.

---

## 1. Headline changes vs v0

| Change | Driver | v0 form | v0.2 form |
|---|---|---|---|
| **K becomes a lattice** | RQ9 + neural-gtm misfit | fixed taxonomy of 7 classes | 7 frozen bootstrap classes + 4 derivation operators, depth ≤ 3 |
| **Seam invariants fold into IC3** | RQ10 + v0.1.1 two-layer split | seam enforced in QA agent only | IC3 gains a clarifying asymmetric-flow clause; manifest gains `layer` + `secret_classes` fields |
| **Two-layer split = conditional default** | RQ12 + Buuuk measurement | not addressed | split when R1 (N≥2 tenants) ∨ R2 (engine stable, churn ≤25%) ∨ R3 (cross-cutting ≤30%) |
| **`SCOPES` becomes K-parametric** | v0.1.1 personal-twin avalanche | constant outbound lexicon hardcoded in solver | per-K SCOPES registry indexed by K_class |
| **3 new primitive ops** | v0.1.1 personal-twin (5,313-primitive output) | 9 ops | 12 ops: + `BULK_UPDATE_MANIFEST`, `CONSOLIDATE_DUPLICATE`, `LINK_INTEGRITY_SCAN` |
| **8th axis `c_privacy` opened as RQ11b** | v0.1.1 PII heuristic misfires | 7 axes | 7 axes; `c_privacy` is a candidate axis for v0.3, not promoted yet |

Everything else in v0 (the function signature, the 3 ICs minus the IC3 clarification, the Z3 hybrid-COP solver, the S(M,T) reduction, the I/L/T enrichments, the K-class archival policy table) stays.

---

## 2. K as a lattice (RQ9 close)

### Recommendation

Replace v0 §5's "K is one of 7 named classes" with:

> **K is an element of a derivation lattice rooted in 7 bootstrap classes.** New K-profiles are produced by composing four formal operators over the bootstrap set. Derivation expressions are explicit (never inferred), depth-capped at 3, and reviewed once by an engineer before entering production solver runs. The bootstrap set is frozen.

### Bootstrap (unchanged)

The 7 v0 classes: `outbound-pipeline`, `content-pipeline`, `product-marketing`, `product-saas`, `research-memory`, `audit-pipeline`, `intel-pipeline`.

### Four operators

```
lift_tenant(K) -> K_engine
    Promotes tenant-specific constraints in H_K and W_K to tenant-agnostic
    "substrate" form. Drops F_K[tenant_specific_failures]; adds F_K[
    interface_compatibility, downstream_breakage]. W_K shifts weight from
    c_money toward c_modify (tenants pay money, engines pay interface
    stability). E_K gains "tenant data, tenant secrets".
    Example: neural-gtm = lift_tenant(outbound-pipeline)

restrict_scope(K, predicate) -> K_subset
    Narrows H_K to a sub-domain via a predicate over scope facts.
    W_K is preserved; T_K may shrink (fewer required tools); E_K may grow.
    Example: outbound-pipeline restricted to "B2B-only, SMTP-only"

compose(K1, K2) -> K_hybrid
    Combines two profiles: union H, weighted-mix W, union T, union F, union E.
    Hard constraints never get blended (union, not average).
    Example: content-pipeline ∘ audit-pipeline = "content-with-provenance" (LSD,
    Healome research-memory variants).

specialize_tenant(K_engine, T) -> K_tenant
    Inverse of lift_tenant. Re-binds engine-shaped K to a specific tenant T,
    re-injecting the tenant-specific constraints. Used to derive the tenant K
    from an engine K when a new tenant joins.
    Example: specialize_tenant(neural-gtm, MAIKAI) gives the MAIKAI-specific
    outbound-pipeline-tenant profile.
```

### Lattice properties

- **Soundness:** each operator preserves well-formedness of (H, W, T, F, E). Verified per-operator by type-checking the output tuple.
- **Identity:** `restrict_scope(K, true) = K` and `compose(K, K) = K` (idempotent in the trivial cases).
- **Non-commutativity:** `compose` is order-sensitive in W_K weights; the spec mandates explicit weight specification on every `compose` call.
- **Depth cap:** ≤ 3 hops from a bootstrap class. Any project requiring depth > 3 triggers a v0.3 RQ.

### Simplicity prior recovery

The H_simp regularizer (inherited from S(M,T)) attaches to the bootstrap class at the root of any derivation chain. Derived classes inherit unless the derivation expression explicitly overrides. Free-form per-folder declaration is forbidden in v0.2; this stays as a possible v0.3 escape hatch.

### Empirical fit on the 8 Neural projects (depth ≤ 1 covers all)

| Project | v0 fit | v0.2 derivation |
|---|---|---|
| Buuuk | outbound-pipeline | outbound-pipeline |
| neural-gtm | none (forced) | `lift_tenant(outbound-pipeline)` |
| Longevity-Science-Daily | hybrid forced | `compose(content-pipeline, product-saas, w=0.65/0.35)` |
| TUHH dashboard | product-saas with caveats | `restrict_scope(product-saas, predicate=internal-only)` |
| Personal Twin | research-memory | research-memory |
| Sheetal GS Engine | audit-pipeline | audit-pipeline |
| si-global-intel | intel-pipeline | intel-pipeline |
| MAIKAI | product-marketing | `compose(product-marketing, product-saas, w=0.7/0.3)` |
| Healome | hybrid forced | `compose(research-memory, content-pipeline, w=0.6/0.4)` |

### Falsifiers

A project requiring an operator outside the four (e.g., `quotient_scope` or `closure`) forces a v0.3 spec edit. A project requiring depth > 3 forces a depth-cap rethink.

### COP encoding impact

`impl/a_star/solver/model.py` gains a `K_resolver` that takes a derivation expression and returns the materialized `(H, W, T, F, E)` tuple by traversing the lattice. The Z3 model itself is unchanged — it consumes the materialized tuple identically to v0.1.

---

## 3. Seam invariants fold into IC3 (RQ10 close)

### Recommendation

Placement (c) wins on three independent literature convergences (Parnas/hexagonal/onion/clean, BLP/Biba/Goguen-Meseguer, ocap/SES/seL4) and four engineering instantiations (Kubernetes CRD/operator, WordPress core/plugin, Postgres extensions, Chrome site isolation). Scoring: (c) 30/35, (b) 17/35, (a) 8/35.

### Precise A_STAR_v0.md diff

**Replace IC3 (v0 §3, line 63):**

> *Old:* "Every stable folder that functions as a navigation, ownership, lifecycle, or execution boundary declares a manifest containing: scope, exclusions, allowed artifact types, owner, lifecycle status, required metadata, outbound relations, and review cadence."

> *New:* "Every stable folder that functions as a navigation, ownership, lifecycle, or execution boundary declares a manifest containing: scope, exclusions, allowed artifact types, owner, lifecycle status, required metadata, outbound relations, review cadence, **layer label `{engine, tenant_<id>, shared}`, and `secret_classes` declaration**. **Inter-folder access is constrained by these labels: a transition originating in a folder labeled `tenant_<id>` may not write paths owned by `engine`-labeled folders (no-write-up, Biba * Property); a transition originating in `engine` may not read paths whose folder declares `secret_classes` ≠ ∅ (BLP Simple Security cut). These are theorems of IC3, not separate constraints.**"

**Add §5 note (after the hybrids paragraph):**

> "For K profiles derived via `lift_tenant`, the resulting engine-K's manifest schema requires `layer: engine` on every folder. For `specialize_tenant`, the resulting tenant-K's manifest requires `layer: tenant_<id>` on tenant-owned folders. `shared` is reserved for cross-tenant infrastructure that the engine vends to all tenants."

**Add §9 footnote on `UPDATE_MANIFEST`:**

> "An `UPDATE_MANIFEST` op that introduces or changes a folder's `layer` label triggers a validator re-run across all sibling and downstream folders to confirm the new label does not break the IC3 asymmetric-flow theorems."

**Add to manifest schema (`impl/a_star/manifest/schema.py`):**

```yaml
layer:
  type: string
  enum: [engine, "tenant_*", shared]
secret_classes:
  type: array
  items:
    type: string
    examples: [api_keys, pii, credentials, oauth_tokens]
```

### Generalization

The same machinery handles five other seams without further axioms:
- `dev/prod` (label = environment)
- `public/private` (label = visibility)
- `human-edited/machine-generated` (label = authorship)
- `billable/non-billable` (label = cost-attribution)
- `PII/non-PII` (label = data classification, partly subsumed by `secret_classes`)

### S(M, T, L) reduction

When `K` is read as `(K_class, layer)`, the v0 reduction `argmax_M S(M, T) = A*(I, L, K=routing, T)` is unchanged. Layer is absorbed into K. No new RQ8 work needed.

### Falsifiers

A seam that requires read/write asymmetry NOT expressible as a BLP/Biba label (e.g., a quantitative budget seam where Layer A may consume up to X% of Layer B's compute) forces a return to placement (a) or (b).

---

## 4. Two-layer split as conditional default (RQ12 close)

### Recommendation

A* recommends two-layer separation for K_class profiles where **any of three rules** holds:

```
R1 (multi-tenant): N_tenants >= 2
R2 (engine-stability): engine_test_pass_rate >= 95% for >= 4 consecutive weeks
                       AND engine_code_churn_rate <= 25%
                       (where churn = lines_changed / lines_total per week)
R3 (low-coupling):    cross_cutting_commit_fraction <= 30%
                       (commits touching both engine and tenant code)
```

The Buuuk/neural-gtm 2026-05-22 split is **validated** under R2 and R3 (R1 false today: only Buuuk; will trip when MAIKAI or Healome adopt the engine).

### Per-axis expected delta for two-layer K

| Axis | Direction | Magnitude (literature-grounded) |
|---|---|---|
| c_drift | ↓ better | -30% to -50% (Mozilla post-modularization, MacCormack/Baldwin/Rusnak) |
| c_modify (within-layer) | ↓ better | -20% to -40% (D'Ambros/Lanza change-coupling) |
| c_modify (cross-layer) | ↑ worse | +50% to +100% per cross-cutting change (Fowler MicroservicePremium) |
| c_loss | ↓ better | -40% to -70% (Reis et al Chrome Site Isolation analog) |
| c_storage | ↑ worse | +10% to +15% (measured 45→51.2 MB on Buuuk: +13%, in band with Reis 9-13%) |
| c_money | flat / slightly ↑ | +0% to +5% (extra CI runners, duplicated venvs) |
| c_find | depends | better within-layer; worse for cross-cutting code-search |
| c_derive | flat | (engine and tenant derivations are mostly independent) |

### Net verdict for Buuuk

Split is **net-positive on 5 of 7 axes**. The c_modify rise affects only cross-cutting commits (today ~12% of Buuuk commits, well below the 30% R3 ceiling). Net cost is reduced.

### Inverse rule (when to collapse)

A* recommends collapsing a two-layer split back into one when, **simultaneously**:
- cross-cutting commit fraction exceeds 40% over a 6-week window
- AND engine churn rises above 35%
- AND there is no second tenant

Read this as: the engine is not stable enough to justify substrate status, and there's no multi-tenant pressure. Collapse, re-evaluate K at single-repo scope.

### Multi-tenant scaling

Per-axis cost as N tenants grows:

```
c_modify(N) ~ c_modify(1) + alpha * sqrt(N)        // cross-cutting touches all N
c_drift(N) ~ c_drift(1) / N                        // engine drift amortizes
c_loss(N) ~ c_loss(1) / N                          // blast-radius confined
c_storage(N) ~ c_storage(1) * (1 + (N-1) * beta)   // tenant duplicates scale linearly with small constant
```

Seam pays off at **N >= 2**. Engine bifurcates (split engine into two engines) when any tenant's required H_K diverges from the engine's H_K by more than `compose` can reconcile, typically around `N = 5-7`.

### Falsifiers

If post-split Buuuk measurements over the next 4 weeks show c_modify_cross_layer > +100% AND c_drift no better than -10%, R2 is violated and the split is provisional. Re-evaluate.

---

## 5. New primitive ops (driven by v0.1.1 personal-twin)

Adds 3 ops to the 9-op set, bringing the total to **12 primitive operations**:

### `BULK_UPDATE_MANIFEST`

Covers a subtree under a single primitive instead of emitting one `UPDATE_MANIFEST` per folder. Required to avoid the 5,313-primitive avalanche personal-twin produced.

```
inputs: root_path, manifest_patch, recurse_depth, schema_validation: strict|stub
effect: applies patch to every folder under root_path satisfying recurse_depth
pre: target subtree has consistent K_class
post: every covered folder has manifest satisfying schema
reversibility: yes (inverse = BULK_UPDATE_MANIFEST with inverse patch)
violates_if_misused: IC3 (if subtree spans K classes)
typical_K: research-memory, content-pipeline (high-cardinality folder trees)
```

### `CONSOLIDATE_DUPLICATE`

Richer than `SET_SOURCE_OF_TRUTH`: identifies near-duplicate artifacts across folders, picks the canonical, links the others as derived. Required for IC1 cleanup in research-memory where context drifts across `memory/projects/*` and `memory/contexts/`.

```
inputs: duplicate_set (list of paths), canonical_choice, similarity_threshold
effect: marks canonical, marks others as derived_from with provenance edges
pre: similarity_score >= threshold across the set
post: IC1 holds within the duplicate_set's scope
reversibility: yes (inverse = re-promote each derived to canonical)
violates_if_misused: IC1 (wrong canonical choice)
typical_K: research-memory, audit-pipeline
```

### `LINK_INTEGRITY_SCAN`

Surrogate for c_loss in memory-class K. Walks artifacts looking for dead links (markdown links, manifest `outbound_relations`, code imports), reports broken ones, emits remediation `UPSERT_RELATION` ops.

```
inputs: root_path, link_patterns (regex list), repair_mode: report|propose|auto
effect: emits diagnostics + optional remediation transaction
pre: link_patterns covers the K's typical link forms
post: dead-link rate measured; remediation queue populated
reversibility: read-only in report mode; remediation ops reversible
violates_if_misused: none (read-only by default)
typical_K: research-memory, content-pipeline (high link density)
```

---

## 6. K-parametric SCOPES (driven by v0.1.1 personal-twin)

`impl/a_star/solver/introspect.py` currently hardcodes SCOPES as the outbound-pipeline lexicon (`lead_records`, `delivery_proof`, etc.). v0.2 makes SCOPES a registry indexed by K_class:

```python
SCOPES = {
    "outbound-pipeline": ["lead_records", "delivery_proof", "consent_receipt", "suppression_record", ...],
    "research-memory":   ["project_context", "capture_partial", "identity_record", "embedding_corpus", "consent_record", ...],
    "content-pipeline":  ["draft", "publication", "source_doc", "rights_record", "review_signoff", ...],
    "audit-pipeline":    ["workpaper", "evidence", "review_artifact", "signoff_record", ...],
    # ... etc per K
}
```

For derived K (lattice form), SCOPES is the union of the base classes' SCOPES, minus what `restrict_scope` predicates exclude.

### PII heuristic tightening (also driven by v0.1.1)

`introspect.py`'s PII detector currently uses substring match (`Contact`, `Doctor`, etc.) and false-fires on HuggingFace model names. v0.2 uses lexeme-boundary regex plus a small "model-name allowlist" to suppress known scientific-corpus directory patterns.

---

## 7. Open RQs that survived v0.2

| RQ | Status | Why deferred |
|---|---|---|
| **RQ11b** — 8th axis `c_privacy` | candidate, not promoted | needs empirical signal that privacy cost has independent variance from c_storage and c_loss; v0.2 keeps 7 axes |
| **RQ13** — folder decay rate λ_K | skeletal | needs the git-mining tool; ~4-week project |
| **RQ14** (new) — composition operator order sensitivity | new | RQ9 close noted `compose` is non-commutative in W_K weights; empirical study needed |
| **RQ15** (new) — when does engine bifurcate? | new | RQ12 close suggests N=5-7, no measurement yet |

---

## 8. Implementation roadmap

| Step | Owner | Effort | Blocks |
|---|---|---|---|
| Add `layer` + `secret_classes` to manifest schema + validator | impl | 0.5 day | nothing |
| Build `K_resolver` (lattice traversal) in `solver/model.py` | impl | 1 day | nothing |
| Implement K-parametric SCOPES registry | impl | 0.5 day | nothing |
| Implement `BULK_UPDATE_MANIFEST` op + planner integration | impl | 1 day | nothing |
| Implement `CONSOLIDATE_DUPLICATE` op | impl | 1.5 days | similarity-scoring helper |
| Implement `LINK_INTEGRITY_SCAN` op | impl | 1 day | regex library for link patterns |
| Migrate QA agent seam invariants to IC3-derived check | qa-agent | 0.5 day | manifest schema update |
| Wire R1/R2/R3 decision rule into A* recommendation output | impl | 1 day | nothing |
| Re-run solver on Buuuk + neural-gtm + personal-twin with v0.2 | validation | 0.5 day | all above |

Total: ~7-8 engineer-days. No external dependencies beyond what v0.1 already needs.

---

## 9. What v0.2 explicitly does NOT change

- The function signature `A*(I, L, K, T) → (A, D)`.
- The 7 axes of C_core.
- ICs 1 and 2 (only IC3 gets a clarification).
- The Z3 hybrid-COP solver shape.
- The S(M, T) reduction proof.
- The I_resilience, I_creativity, T_onboard, T_reverse, T_devex enrichments.
- The per-K archival policy table.
- The 7 bootstrap K classes (they freeze; only derivations are new).

---

## 10. Honest limits (carried forward)

- v0.2 closes the spec but the lattice derivation rules have ONE worked example (`lift_tenant(outbound-pipeline) = neural-gtm`). The other 8 entries in the empirical fit table are spec-correct but not implementation-verified.
- The decision rule R1/R2/R3 has thresholds (95%, 25%, 30%, 4 weeks) calibrated from literature, not from A*'s own measurement loop. Recalibrate after 8 weeks of Buuuk operation.
- `c_privacy` candidacy is open. If personal-twin's PII heuristics keep misfiring after the lexeme-boundary fix, the axis gets promoted.
- The 12-op set is hypothesized minimal-complete for K = {outbound, research-memory}. The other 5 K classes may surface ops we haven't seen yet.

---

## 11. Outputs in this release

- `A_STAR_v0_2.md` (this document)
- `research/wave4/RQ9-k-class-form.md` (61.7 KB, K lattice argument, 10+ cited works)
- `research/wave4/RQ10-seam-as-primitive.md` (49.2 KB, IC3 derivation argument, 25 cited works)
- `research/wave4/RQ12-seam-cost.md` (57.6 KB, conditional-default argument, 30 cited works)
- `protocols/wave4_threads.json` (the original thread specs; ran via Claude Code native deep search instead of Parallel.ai)
- `protocols/wave4_state.json` (Parallel.ai launch attempt log, kept for audit; HTTP 402 reason recorded)

Total wave 4 research output: ~168 KB.
Total wave 4 cost: $0 (Claude Code native, no API spend).

---

## 12. v0.2 → v0.3 sketch

v0.3 will close one or more of:
- RQ11b promotion of `c_privacy` to 8th axis (after privacy data lands).
- RQ13 folder decay measurement (after the git-mining tool).
- RQ14 composition order sensitivity (after the second hybrid project ships).
- A second worked-impl on a non-outbound K (LSD content-pipeline or Personal Twin research-memory).

No spec close on v0.3 before either: (a) the 4-week Buuuk/neural-gtm measurement window completes and confirms or falsifies the R1/R2/R3 thresholds, or (b) a second tenant joins the neural-gtm engine and exercises `specialize_tenant`.
