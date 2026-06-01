# A* v0 Routing Reduction and Primitive Outputs

## Executive Summary

- **Routing Reduction**: `S(M,T)` has **3 factors** - gates, weighted utilities, and a simplicity prior - while A* has **7 C_core axes** and a **6-part T vector** by the v0 specification -> define `S(M,T)` as the `K = routing` profile of A*, not as a separate architecture function.

- **Objective Collapse**: Z3 Optimize supports weighted soft constraints, objective functions, and **3** objective-priority modes - lexicographic, Pareto, and box Soft Constraints | Online Z3 Guide [56] Combining Objectives | Online Z3 Guide [24] Z3 Optimize API [54] -> implement `S(M,T)` as one scalarized Optimize objective only when structural degrees of freedom are fixed.

- **Simplicity Prior**: MDL, Solomonoff induction, AIC/BIC, dropout, Parnas information hiding, and architecture quality-attribute theory all penalize unnecessary complexity MDL Tutorial [3] Solomonoff [28] Burnham and Anderson [27] Parnas [76] -> add `H_simp` to A* as a soft regularizer, not as a hard constraint.

- **Strict Generalization Boundary**: `S(M,T)` returns a selected model or route, while A* must emit an architecture state, diagnostics, and executable deltas -> use the reduction only for fixed-folder, fixed-persistence routing decisions.

- **Primitive Minimality**: The **17** candidate primitive names in the prompt compile cleanly to **9** v0 primitives -> keep the solver output small, machine-executable, reversible where required, and use macros for split, merge, rename, tagging, and promotion.

- **Migration-Tool Pattern**: Alembic, Django, Prisma, Liquibase, and Flyway converge on versioned operations, upgrade/downgrade or reverse logic, rollback, and migration history Alembic Operations [59] Django Migration Operations [39] Prisma Down Migrations [40] Liquibase Rollback [43] Flyway Migrations [14] -> A* should emit a transaction with a primitive plan and rollback plan, not a naked final state.

- **Knowledge-Architecture Pattern**: PARA uses **4** top-level categories, medallion architecture uses **3** refinement layers, and the GoF design-patterns book catalogs **23** recurring patterns PARA Method [16] Databricks Medallion Architecture [64] Design Patterns [45] -> make archive, promote, cache, manifest, and relation updates first-class architecture operations.

- **Semantic Versioning Risk**: Ontology evolution literature distinguishes change logs, structural diffs, and minimal transformation sets Klein and Noy [37] -> A* should store both the human audit log and the minimal machine-executable transformation set.

- **Closing Gaps**: v0 still needs policies for incremental tuning vs full re-derivation, operator overrides, observed-cost learning, infeasibility diagnostics, permission boundaries, and self-versioning -> flag these as synthesis blockers before freezing the A* v0 document.

## Part A - `S(M,T)` Is the Routing-Profile Special Case of A*

### The substitution map makes `M` a degenerate architecture candidate

The clean way to close the formal gap is to treat routing as a restricted A* profile. Let:

```text
x = (I, L, K, T)
Omega(x) = architecture candidates available under input x
A in Omega(x) = one candidate architecture
C_core(A,x) = <c_1(A,x), ..., c_7(A,x)>
G_j(A,x) in {0,1} = hard integrity constraint j
```

The prompt names `c_modify` and `c_drift` but does not name all **7** `C_core` axes. In this memo, `c_1 ... c_7` are placeholders for the canonical v0 axis names. Where a concrete regularizer is needed, I use `c_modify` and `c_drift` because the prompt identifies them as likely compatible with `H_i`.

| `S(M,T)` term | A* term | Formal substitution | Design meaning |
|---|---|---|---|
| `M` | `A_M` | `M <-> A_M`, where `A_M` is an architecture candidate whose only free decision is selected model or route | A model is a degenerate architecture. |
| `T` | `(I,L,K,T)` | `T_route <-> x = (I,L,K = routing,T)` | Routing context becomes the full A* input bundle. |
| `gate_j(M,T)` | `G_j(A_M,x)` | `gate_j(M,T) = 1 iff G_j(A_M,x) = 1` | Must-have routing gates become hard integrity constraints. |
| `prod_j gate_j` | Feasibility filter | `prod_j gate_j = 1 iff all G_j = 1` | A failed gate is an infeasible architecture. |
| `phi_i(M,T)` | Negative cost utility | `phi_i(A_M,x) = norm_i(-c_i(A_M,x))` | Soft routing features are normalized benefits from lower architecture cost. |
| `w_i` | Soft objective weights | `w_i = lambda_i(K,T)` | Weights are profile-calibrated by constraint class and task vector. |
| `H_i(M,T)` | `H_simp(A_M,x)` | `H_simp` is a function of complexity, entropy, `c_modify`, and `c_drift` | The routing simplicity prior becomes an architecture regularizer. |
| `beta` | Regularization strength | `beta = beta(K,T)` | Simplicity pressure varies by lifecycle and profile. |

Z3 supports this representation because Optimize can combine hard constraints with objective functions and weighted soft constraints Soft Constraints | Online Z3 Guide [56] Z3 Optimize API [54]. Its support for lexicographic, Pareto, and box objective modes also means A* does not have to collapse all profiles to a single scalar when that would hide trade-offs Combining Objectives | Online Z3 Guide [24].

### The reduction proof uses fixed structure and one remaining decision variable

Start from the general A* constrained optimization problem:

```text
A*(I,L,K,T) = arg opt over A in Omega(I,L,K,T)
              subject to G_j(A,I,L,K,T) = 1 for all j
              optimizing C_core(A,I,L,K,T) and diagnostics D
```

Now impose the routing restriction:

```text
K = routing
folder_structure = F_0
naming_scheme = N_0
archival_policy = R_0
persistence_layer = P_0
```

Under these restrictions, A* no longer searches over folders, names, archive rules, or persistence locations. Its candidate set collapses to:

```text
Omega_routing(x) = {A_M : M in candidate_models(T)}
```

Each `A_M` differs only by the selected model or route. The hard constraints become routing gates:

```text
G_j(A_M,x) = gate_j(M,T)
```

Therefore:

```text
A_M is feasible under A*
iff all G_j(A_M,x) = 1
iff prod_j gate_j(M,T) = 1
```

Next convert costs to utilities:

```text
phi_i(A_M,x) = norm_i(-c_i(A_M,x))
U(A_M,x) = sum_i w_i * phi_i(A_M,x)
```

Then add a simplicity term compatible with `c_modify` and `c_drift`:

```text
H_simp(A_M,x) =
  alpha_modify * c_modify(A_M,x)
  + alpha_drift * c_drift(A_M,x)
  + alpha_struct * structural_entropy(A_M,x)
  + alpha_rel * relation_count_penalty(A_M,x)
```

The restricted A* scalar objective is:

```text
Score(A_M,x) =
  [prod_j G_j(A_M,x)]
  * [sum_i w_i * phi_i(A_M,x)]
  * exp(-beta * H_simp(A_M,x))
```

Substituting `G_j(A_M,x) = gate_j(M,T)` and `A_M <-> M` yields:

```text
Score(A_M,x) = S(M,T)
```

Thus:

```text
argmax_M S(M,T) = A*(I,L,K = routing,T)
```

provided that the architecture search space is fixed except for model or route selection.

If `U(A_M,x) > 0`, the multiplicative score can also be implemented as the monotone log objective:

```text
log U(A_M,x) - beta * H_simp(A_M,x)
```

That is useful because Optimize can maximize rational or arithmetic expressions without needing to reason directly about `exp`. If utilities can be zero or negative, v0 should either shift utilities into a positive range or precompute the scalar score outside Z3 and expose it as a fixed-point objective.

### Five cases where the reduction is not valid

| Boundary condition | `S(M,T)` can express it? | A* can express it? | Why it matters |
|---|---:|---:|---|
| Discrete structural outputs | No | Yes | `S` chooses a model; A* creates, moves, archives, and annotates architecture artifacts. |
| Multi-objective trade-offs | Weakly | Yes | Z3 supports lexicographic, Pareto, and box objective handling Combining Objectives | Online Z3 Guide [24]. A scalar score can hide non-dominated alternatives. |
| Hard constraints with side effects | No | Yes | A gate can say "reversible", but A* must emit archive, manifest, inverse, and validation operations. |
| Lifecycle-stage modulation | Usually folded into features | Yes | `T_human`, `T_agent_internal`, `T_agent_external`, `T_onboard`, `T_reverse`, and `T_devex` can change both constraints and weights. |
| Team-vector enrichment | No | Yes | The same architecture can have different onboarding or devex costs for different teams. |

The failure case is not a flaw in the reduction. It defines its boundary. `S(M,T)` is a decision rule over fixed candidates; A* is a discrete architecture synthesis and execution-planning function.

### Simplicity should flow back into A*

The strongest concept to import from `S(M,T)` is the explicit simplicity prior. The MDL principle selects the model that minimizes the description length of the model plus the data encoded with the model MDL Tutorial [3]. Solomonoff induction gives the deeper Occam-style prior by assigning higher prior weight to shorter algorithmic descriptions Solomonoff [28]. AIC and BIC are model-selection criteria that balance fit and complexity Burnham and Anderson [27].

Machine-learning regularization provides a practical analogy. Dropout reduces overfitting by randomly dropping units and their connections during training Dropout JMLR [50]. A* should not literally use dropout, but the architectural analogy is direct: avoid solutions that work only because of brittle special-case dependencies.

Software architecture adds the domain-specific reason. Parnas argued that modularization should improve flexibility and comprehensibility through information hiding Parnas [76]. Bass, Clements, and Kazman frame architecture as the enabler of quality attributes such as modifiability, testability, deployability, availability, and performance SEI Quality Model [48]. The Gang of Four design-patterns catalog also shows the value of named reusable structures over ad hoc reinvention Design Patterns [45].

Recommended v0 regularizer:

```text
H_simp(A,x) =
  alpha_1 * structure_count(A)
  + alpha_2 * relation_count(A)
  + alpha_3 * manifest_entropy(A)
  + alpha_4 * c_modify(A,x)
  + alpha_5 * c_drift(A,x)
```

Use it in **3** places, with different strengths:

| Placement | Role | Recommendation |
|---|---|---|
| Soft objective in `C` | Visible to Optimize and diagnostics | Default placement. |
| Search regularizer | Prunes candidates that add unnecessary structure | Use cautiously to avoid blocking creative candidates. |
| Pareto tie-breaker | Chooses simpler candidates among non-dominated states | Always safe as a final tie-break. |

Decision: add `H_simp` as a soft objective and Pareto tie-breaker. Do not make it a hard integrity constraint, because archive trails, manifests, and lineage edges may look complex while being required for reversibility.

### Precise v0 definition

Recommended definition:

```text
A* is a constrained architecture synthesis function that maps
(I, L, K, T) to an architecture state A and diagnostics D by selecting
or constructing discrete structural decisions over folder structure,
naming scheme, archival policy, manifest metadata, source-of-truth
registration, and persistence routing, subject to hard integrity
constraints and profile-calibrated soft objectives over C_core.

The routing score S(M,T) is the special case of A* obtained when
K = routing; folder structure, naming scheme, archival policy, and
persistence layer are fixed; the only free decision is the selected
model or route M; routing gates are hard integrity constraints;
C_core costs are converted into weighted positive utilities phi_i;
and an optional simplicity regularizer H_simp is applied
multiplicatively or by an equivalent monotone log transform.
```

## Part B - Literature Survey Behind the Primitive Set

### Nine source families converge on state-plus-delta architecture change

The literature does not provide one perfect catalog of "folder architecture primitives", but several mature domains converge on the same pattern: named operations, versioned state transitions, validation, reversibility, and audit.

| Source family | Relevant evidence | A* design implication |
|---|---|---|
| Fowler refactoring catalog | Fowler's catalog gives named transformations such as extract, move, rename, and inline Refactoring Catalog [6]. | Use named operations, but adapt code-level refactorings to architecture-level artifacts. |
| Refactoring research | Mens and Tourwe survey refactoring as structural improvement, while evolutionary architecture research uses automated planning to generate refactoring sequences A Survey of Software Refactoring [8] Software Evolutionary Architecture [7]. | A* should output a sequence or plan, not only one operation. |
| Schema migration | Alembic uses operations in `upgrade()` and `downgrade()`; Django uses declarative operations with reverse logic; Prisma supports down migrations; Liquibase supports rollback; Flyway uses versioned and undo migrations Alembic Operations [59] Django Migration Operations [39] Prisma Down Migrations [40] Liquibase Rollback [43] Flyway Migrations [14]. | A* primitives need pre-conditions, post-conditions, and inverse or rollback semantics. |
| Folder restructuring | Git `mv` moves or renames files, directories, or symlinks Git mv [63]. | Treat rename as a special case of move. |
| Knowledge organization | PARA organizes digital material into Projects, Areas, Resources, and Archives PARA Method [16]. Zettelkasten processes fleeting notes into permanent linked notes or discards/archive them Zettelkasten Note Types [69]. | Include archive, promote, tag, and relation operations. |
| Database normalization | Normalization organizes tables to improve integrity, prevent anomalies, and minimize redundancy IBM Database Normalization [72]. | Split overloaded containers when redundancy or ambiguity creates drift. |
| Denormalization | Denormalization reintroduces redundancy to improve read performance DataCamp Denormalization [66]. | Allow derived cache copies, but mark them non-canonical. |
| Medallion architecture | Databricks describes Bronze, Silver, and Gold layers for progressive data refinement Databricks Medallion Architecture [64]. | Model source, cleaned, and derived layers explicitly. |
| Ontology evolution | Stojanovic and Motik discuss elementary and composite ontology changes; Klein and Noy distinguish logs, diffs, and minimal transformation sets Stojanovic and Motik [60] Klein and Noy [37]. | Emit minimal transformation sets while preserving full audit logs. |

The decision-ready insight is that A* should be neither a pure scorer nor a pure file-manipulation script. It should be a constrained planner that emits the smallest sufficient transformation set, backed by audit metadata.

### Local adapters for the missing v0 names

The prompt says A* has **7** `C_core` axes and **7** `K` classes, but it names only `c_modify`, `c_drift`, `K = routing`, and a Buuuk-class example. To keep the primitive table precise without inventing canonical names, this memo uses local adapters.

Local `C_core` reporting adapter:

```text
C7 = [
  c_find,
  c_modify,
  c_integrity,
  c_reverse,
  c_drift,
  c_storage,
  c_devex
]
```

Local `K` adapter:

```text
K_route
K_human
K_agent_internal
K_agent_external
K_onboard
K_reverse
K_devex
```

Replace these with the canonical Wave 1-3 names if they differ. The primitive semantics do not depend on the labels.

Local integrity-constraint adapter:

```text
IC1 - Canonicality:
  every governed artifact has exactly one source of truth, or an explicit
  derived/cache/exception status.

IC2 - Reversibility:
  state-changing operations are reversible, archived, or explicitly scheduled
  as irreversible with approval.

IC3 - Manifest Consistency:
  folders, artifacts, metadata, persistence routes, and graph relations match
  the manifest and can be executed by an agent or script.
```

### Recommended minimal primitive set has 9 operations, not 17

Recommended solver-emitted primitives:

1. `CREATE_FOLDER`
2. `ARCHIVE_FOLDER`
3. `MOVE_ARTIFACT`
4. `DUPLICATE_TO_CACHE`
5. `SET_SOURCE_OF_TRUTH`
6. `UPDATE_MANIFEST`
7. `UPSERT_RELATION`
8. `MIGRATE_PERSISTENCE`
9. `SCHEDULE_DESTRUCTION`

The remaining candidates become macros or typed instances:

| Candidate operation | v0 treatment | Reason |
|---|---|---|
| `RENAME_ARTIFACT` | Macro over `MOVE_ARTIFACT` | Git treats move and rename as one operation family Git mv [63]. |
| `SPLIT_FOLDER` | Macro: `CREATE_FOLDER` plus `MOVE_ARTIFACT` plus `UPDATE_MANIFEST` | Split is composite. |
| `MERGE_FOLDERS` | Macro: `MOVE_ARTIFACT` plus `ARCHIVE_FOLDER` plus `UPDATE_MANIFEST` | Merge is composite. |
| `PROMOTE_DERIVED_TO_SOURCE` | Macro: `SET_SOURCE_OF_TRUTH` plus optional `MOVE_ARTIFACT` and `UPDATE_MANIFEST` | Promotion changes canonicality and metadata. |
| `REGISTER_SOURCE_OF_TRUTH` | Typed `SET_SOURCE_OF_TRUTH` | Same primitive with `status = registered`. |
| `RETIRE_SOURCE_OF_TRUTH` | Typed `SET_SOURCE_OF_TRUTH` | Same primitive with `status = retired`. |
| `ATTACH_MANIFEST` | Typed `UPDATE_MANIFEST` | Manifest creation is a manifest update from null. |
| `ADD_FACET` | Typed `UPSERT_RELATION` | Facet is a metadata relation. |
| `ADD_TAG` | Typed `UPSERT_RELATION` | Tag is a metadata relation. |
| `ADD_GRAPH_RELATION` | Typed `UPSERT_RELATION` | Graph edge is a relation. |

The minimal set is complete for v0 because it covers the core mutation types: create container, retire container, relocate artifact, create derived copy, change canonicality, change metadata, change graph relations, change persistence backend, and schedule irreversible removal.

### Per-primitive pre-conditions and post-conditions

| Primitive | Inputs | Effect | Pre-conditions | Post-conditions |
|---|---|---|---|---|
| `CREATE_FOLDER` | `folder_id`, `path`, `purpose`, `owner`, optional `manifest_ref` | Creates an addressable container. | Parent exists; path is unused; naming policy passes. | Folder exists; purpose and ownership are recorded or explicitly unmanaged. |
| `ARCHIVE_FOLDER` | `folder_id`, `archive_path`, `reason`, `retention_policy`, `manifest_ref` | Moves an inactive folder to an archive namespace. | Folder exists; no active canonical source is silently hidden. | Archive path exists; old path, new path, reason, timestamp, and restore path are recorded. |
| `MOVE_ARTIFACT` | `artifact_id`, `from_path`, `to_path`, `reference_update_policy` | Moves or renames an artifact. | Source exists; destination is valid; references are discoverable or explicitly scoped out. | Artifact exists at destination; manifest and references are updated or exceptions logged. |
| `DUPLICATE_TO_CACHE` | `source_artifact_id`, `cache_path`, `derivation_rule`, `ttl`, `invalidator` | Creates a non-canonical derived copy. | Source of truth is known; derivation rule exists. | Cache exists; manifest records `derived_from`, TTL, and invalidation rule. |
| `SET_SOURCE_OF_TRUTH` | `artifact_id`, `scope`, `status`, `supersedes`, `reason` | Registers, retires, or promotes canonical authority. | Artifact exists; conflict check passes. | Exactly one canonical source per scope, or an explicit exception exists. |
| `UPDATE_MANIFEST` | `manifest_id`, `patch`, `schema_version`, `validator`, optional `inverse_patch` | Creates or changes manifest metadata. | Patch validates against schema. | Manifest version advances; affected artifacts match metadata. |
| `UPSERT_RELATION` | `subject_id`, `relation_type`, `object_id_or_value`, `operation`, `confidence`, `provenance` | Adds, updates, or removes a tag, facet, lineage edge, dependency, or graph relation. | Subject exists; relation type is allowed; object exists unless literal. | Relation graph validates; provenance is recorded. |
| `MIGRATE_PERSISTENCE` | `artifact_or_collection_id`, `from_backend`, `to_backend`, `mapping`, `verification_query`, `rollback_route` | Moves or reroutes persistence across filesystem, database, object store, vector store, cache, or index. | Source reachable; target provisioned; mapping and verification exist. | Target contains verified data; route manifest points to target; old route is retained or retired by policy. |
| `SCHEDULE_DESTRUCTION` | `artifact_or_folder_id`, `destruction_time`, `retention_policy`, `approver`, `pre_destroy_archive` | Schedules deletion behind a retention and approval gate. | Artifact exists; policy permits destruction; archive requirement is evaluated. | Destruction is pending, not immediate; rollback window and approval are recorded. |

### Per-primitive cost effects, reversibility, integrity risks, and K use cases

Legend: `-` lowers cost, `+` raises cost, `0` is neutral, `+/-` is context-dependent.

| Primitive | C7 effect `[find, modify, integrity, reverse, drift, storage, devex]` | Reversibility | Misuse can violate | Typical K use |
|---|---|---|---|---|
| `CREATE_FOLDER` | `[-, -, +/-, 0, +/-, +, +/-]` | Always reversible if empty; reversible with move/archive if non-empty. | IC3 if manifest is not updated; IC1 if folder implies false authority. | `K_onboard`, `K_devex`, `K_route`, Buuuk source/cache setup. |
| `ARCHIVE_FOLDER` | `[+, -, -, -, -, +/-, -]` | Reversible if archive path and manifest are retained. | IC1 if active source is archived; IC2 if restore path is missing; IC3 if links break. | `K_reverse`, `K_human`, lifecycle closure. |
| `MOVE_ARTIFACT` | `[-, +/-, +/-, 0, +/-, 0, +/-]` | Reversible if original path and reference diff are logged. | IC1 if authority changes accidentally; IC3 if references are stale. | `K_onboard`, `K_devex`, `K_agent_internal`. |
| `DUPLICATE_TO_CACHE` | `[-, +, +/-, +/-, +, +, -]` | Reversible by deleting or archiving cache because source remains. | IC1 if cache is mistaken for source; IC3 if derivation is missing. | `K_agent_external`, `K_devex`, medallion-like derived layer. |
| `SET_SOURCE_OF_TRUTH` | `[-, -, -, +/-, -, 0, +]` | Reversible if prior authority state and old source are retained. | IC1 directly; IC2 if prior source is destroyed; IC3 if manifest diverges. | `K_route`, `K_reverse`, Buuuk source promotion. |
| `UPDATE_MANIFEST` | `[-, -, -, -, -, +/-, +]` | Reversible if inverse patch or prior version is retained. | IC3 directly; IC1 if source metadata is wrong. | All K classes, especially `K_agent_internal` and `K_onboard`. |
| `UPSERT_RELATION` | `[-, +/-, +/-, -, +/-, +, +/-]` | Reversible if old edge value is logged. | IC1 if relation asserts false authority; IC3 if graph becomes inconsistent. | Zettelkasten links, ontology relations, tags, facets, retrieval. |
| `MIGRATE_PERSISTENCE` | `[-, +/-, +/-, +/-, +/-, +/-, +/-]` | Reversible if old backend or export snapshot is retained. | IC1 if authority moves silently; IC2 if rollback route is missing; IC3 if route manifest is wrong. | `K_route`, `K_agent_internal`, `K_agent_external`, scale transition. |
| `SCHEDULE_DESTRUCTION` | `[0, -, +/-, -, -, -, +]` before execution | Reversible before deadline; irreversible after destruction unless archived. | IC2 directly; IC1 if canonical artifact is scheduled; IC3 if schedule is omitted. | `K_reverse`, compliance cleanup, cache expiry, archival hygiene. |

The main trade-off is that operations that improve findability or devex can increase storage, manifest burden, or modification cost. That is why A* should report per-axis deltas instead of hiding them in a single score.

## Composition - A* Should Emit a Transactional Plan, Not One Primitive

A real architecture change is almost always a sequence. `SPLIT_FOLDER`, for example, compiles to `CREATE_FOLDER`, multiple `MOVE_ARTIFACT` operations, `UPSERT_RELATION` updates, and `UPDATE_MANIFEST`. Migration systems validate this approach: Alembic uses upgrade and downgrade functions; Django supports reversible operation definitions; Prisma supports down migrations; Liquibase rolls back to tags; Flyway uses versioned and undo migrations Alembic Operations [59] Django Migration Operations [39] Prisma Down Migrations [40] Liquibase Rollback [43] Flyway Migrations [14].

Ontology evolution points to the same conclusion. Klein and Noy distinguish a full change log from a transformation set, and define the minimal transformation set as the sufficient operations needed to transition between versions Klein and Noy [37]. A* should therefore output the minimal executable transformation set while retaining the full diagnostic trace.

Recommended architecture:

```text
Layer 1 - COP model:
  Z3 Optimize selects target architecture variables.

Layer 2 - Delta compiler:
  Compare A_current to A_target and compile differences into primitives.

Layer 3 - Transaction renderer:
  Topologically sort operations, attach pre-checks, inverse operations,
  rollback plan, validations, diagnostics, and human rationale.
```

Z3 emits a model, not a filesystem migration script. Therefore A* should emit:

```text
A_target + primitive_transaction + diagnostics D
```

not just:

```text
A_target
```

### Operator-facing YAML for a small Buuuk-class transformation

```yaml
a_star_output:
  spec_version: "a-star-v0"
  run_id: "2026-05-21-buuuk-demo"

  input_fingerprint:
    I_hash: "sha256:..."
    L_hash: "sha256:..."
    K: "buuuk"
    T_profile:
      T_human: "high"
      T_agent_internal: "medium"
      T_agent_external: "low"
      T_onboard: "high"
      T_reverse: "high"
      T_devex: "medium"

  solver:
    engine: "hybrid-cop-z3-optimize"
    objective_mode: "lex_then_weighted_sum"
    z3_priority: "lex"
    status: "sat"

  target_architecture:
    folders:
      - path: "knowledge/source"
        purpose: "canonical human-authored source material"
      - path: "knowledge/cache"
        purpose: "derived agent-readable summaries"
      - path: "knowledge/archive"
        purpose: "inactive or superseded material"
    source_of_truth:
      scope: "buuuk/customer-onboarding"
      artifact_id: "artifact.customer_onboarding_md"
      path: "knowledge/source/customer-onboarding.md"
    persistence_routes:
      source: "filesystem"
      cache: "filesystem"
    manifest:
      path: "architecture.manifest.yaml"
      schema_version: "0.1"

  primitive_plan:
    transaction_id: "txn-buuuk-001"
    atomic_commit: true
    rollback_required: true
    operations:
      - id: "op1"
        primitive: "CREATE_FOLDER"
        inputs:
          path: "knowledge/source"
          purpose: "canonical source layer"
        inverse:
          primitive: "ARCHIVE_FOLDER"
          condition: "only_if_empty"

      - id: "op2"
        primitive: "CREATE_FOLDER"
        inputs:
          path: "knowledge/cache"
          purpose: "derived cache layer"
        inverse:
          primitive: "ARCHIVE_FOLDER"
          condition: "only_if_empty"

      - id: "op3"
        primitive: "MOVE_ARTIFACT"
        depends_on: ["op1"]
        inputs:
          artifact_id: "artifact.customer_onboarding_md"
          from_path: "notes/inbox/customer-onboarding.md"
          to_path: "knowledge/source/customer-onboarding.md"
          reference_update_policy: "update_manifest_and_relative_links"
        inverse:
          primitive: "MOVE_ARTIFACT"
          inputs:
            from_path: "knowledge/source/customer-onboarding.md"
            to_path: "notes/inbox/customer-onboarding.md"

      - id: "op4"
        primitive: "SET_SOURCE_OF_TRUTH"
        depends_on: ["op3"]
        inputs:
          artifact_id: "artifact.customer_onboarding_md"
          scope: "buuuk/customer-onboarding"
          status: "registered"
          reason: "source note is canonical for this topic"

      - id: "op5"
        primitive: "DUPLICATE_TO_CACHE"
        depends_on: ["op2", "op4"]
        inputs:
          source_artifact_id: "artifact.customer_onboarding_md"
          cache_path: "knowledge/cache/customer-onboarding.summary.md"
          derivation_rule: "summarize_for_agent_retrieval"
          ttl: "30d"
          invalidator: "source_hash_change"

      - id: "op6"
        primitive: "UPSERT_RELATION"
        depends_on: ["op5"]
        inputs:
          subject_id: "knowledge/cache/customer-onboarding.summary.md"
          relation_type: "derived_from"
          object_id_or_value: "artifact.customer_onboarding_md"
          confidence: 1.0
          provenance: "a-star-v0"

      - id: "op7"
        primitive: "UPDATE_MANIFEST"
        depends_on: ["op1", "op2", "op3", "op4", "op5", "op6"]
        inputs:
          manifest_id: "architecture.manifest.yaml"
          schema_version: "0.1"
          patch:
            add_folders:
              - "knowledge/source"
              - "knowledge/cache"
            register_source:
              scope: "buuuk/customer-onboarding"
              path: "knowledge/source/customer-onboarding.md"
            add_cache:
              path: "knowledge/cache/customer-onboarding.summary.md"
              derived_from: "knowledge/source/customer-onboarding.md"

  expected_C_core_delta:
    c_find: -0.30
    c_modify: -0.10
    c_integrity: -0.25
    c_reverse: -0.05
    c_drift: -0.20
    c_storage: 0.08
    c_devex: -0.12

  constraints_validated:
    IC1_canonicality:
      status: "pass"
      evidence: "one source_of_truth registered for buuuk/customer-onboarding"
    IC2_reversibility:
      status: "pass"
      evidence: "all moves have inverse operations; cache is derived"
    IC3_manifest_consistency:
      status: "pass"
      evidence: "manifest patch covers folders, source, cache, and relation"

  diagnostics:
    D_resilience:
      rollback_plan: "present"
      archive_required: false
      destructive_operations: 0
    D_creativity:
      novelty: "low"
      rationale: "uses source/cache layering without adding a new persistence backend"
    infeasibility:
      unsat_core: []
      violated_soft_constraints: []

  rationale: >
    The transformation separates canonical source notes from derived
    agent-readable cache artifacts. It improves findability,
    source-of-truth clarity, and drift control at the cost of a small
    storage increase.
```

The example uses a medallion-like source/cache distinction, but keeps persistence fixed. That makes it a Buuuk-class transformation rather than a full persistence migration.

## Part C - Closing Gaps Before the v0 Synthesis Document

| Gap | Failure mode if ignored | Recommendation |
|---|---|---|
| Incremental tuning vs full re-derivation | Small weight changes cause architecture churn or inconsistent local patches. | Use incremental tuning when no hard constraint changes and delta cost is below a churn threshold; use full re-derivation for source-of-truth, persistence, or integrity changes. |
| Operator overrides | Humans can force unsafe architectures without traceability. | Allow soft-objective override with reason, approver, and expiry; require waiver plus rollback plan for hard-constraint override. |
| Observed-cost learning | Predicted `C_core` deltas never improve after deployment. | Log predicted vs observed deltas, rollback events, find time, modification time, drift incidents, and agent failures; recalibrate `K`, `T`, weights, and `beta`. |
| A* self-versioning | Future A* changes cannot reproduce old decisions. | Record `spec_version`, solver version, primitive schema version, `C_core` schema version, `K` profile version, and manifest schema version in every run. |
| Infeasibility diagnostics | Solver returns no useful guidance when constraints conflict. | Return no architecture on `unsat`; return failed constraints, relaxations, minimum waiver set, and remediation options. |
| Permission model | Machine-executable operations can modify or destroy state without authority. | Add dry-run, capability manifest, approval gates, and separate permissions for migration, canonicality, and destruction. |
| Measurement of `C_core` | Weights become decorative because axis values are not comparable. | For each axis, define unit, range, normalization, measurement source, confidence, owner, and update cadence. |
| Macro expansion audit | Operators approve `SPLIT_FOLDER` without seeing destructive substeps. | Render macros for humans, but validate and execute the compiled primitive plan. |

The most important unresolved issue is feedback. A* v0 can predict that a folder split lowers `c_find`, but only observed usage can confirm whether humans and agents actually find artifacts faster. The v0 spec should therefore treat deployment outcomes as calibration data, not as anecdotal feedback.

The second major issue is override governance. Architecture functions are advisory until an operator can safely disagree. The correct pattern is not to block disagreement; it is to record why the override happened, which hard or soft constraints were waived, how long the waiver lasts, and how rollback works.

## Synthesis - The Final A* Relationship

| Framework | Mechanism | Output | Scope | Trade-off | A* decision |
|---|---|---|---|---|---|
| `S(M,T)` | Gate product, weighted utility sum, simplicity prior | Selected model or route | Fixed candidates | Simple and explainable, but not structural | Embed as `K = routing`. |
| A* COP | Hard constraints plus multi-objective optimization | Architecture state plus diagnostics | Structural synthesis | Expressive, but needs delta compilation | Use for all non-routing architecture decisions. |
| Simplicity prior | MDL, Solomonoff, AIC/BIC, regularization | Complexity-adjusted objective | Model and architecture selection | Prevents overfit, but can punish necessary audit structure | Add `H_simp` as soft objective and tie-breaker. |
| Primitive transaction | Minimal transformation set with inverse plan | Executable architecture delta | Repo, metadata, persistence, and graph changes | Operationally safe, but more verbose | Emit target state plus primitive transaction. |
| Feedback loop | Observed outcomes recalibrate weights | Updated `K`, `T`, `beta`, and cost priors | Post-deployment learning | Improves accuracy, but requires governance | Version and audit all learning. |

The core tension is scalar elegance vs operational accountability. `S(M,T)` is powerful because it compresses routing into one number. A* cannot stop there because architecture decisions produce side effects: files move, folders appear, manifests change, caches are derived, sources of truth are registered, and rollback obligations are created.

The second tension is simplicity vs reversibility. A pure simplicity prior would penalize archives, manifests, and lineage edges because they add structure. But those structures are often what make an architecture safe. Therefore `H_simp` should penalize unnecessary complexity, not necessary auditability.

Final closing statement:

```text
A* generalizes S(M,T) from scalar candidate routing to constrained,
diagnosed, and executable architecture synthesis. Routing is recovered
when the architecture search space is restricted to fixed-structure
model candidates and the A* objective is scalarized into the gated,
weighted, simplicity-regularized score S. Outside that restriction,
A* emits structural target states and primitive transactions over
folders, artifacts, metadata, source-of-truth registrations, archival
policy, and persistence routes, while preserving hard integrity
constraints and exposing diagnostics for human and agent operators.
```

## References

1. *Akaike information criterion - Wikipedia*. https://en.wikipedia.org/wiki/Akaike_information_criterion
2. *Model Selection Using the Minimum Description Length Principle*. https://www.jstor.org/stable/2685777
3. [[PDF] A Tutorial Introduction to the Minimum Description Length Principle](http://homepages.cwi.nl/~paulv/course-kc/mdlintro.pdf)
4. *Objective Optimization | Z3Prover/z3 | DeepWiki*. https://deepwiki.com/Z3Prover/z3/4.3-objective-optimization
5. *Information criteria: How do they behave in different models?*. https://www.sciencedirect.com/science/article/pii/S0167947313002776
6. *Using the Catalog - Refactoring*. https://refactoring.com/catalog/
7. *Software evolutionary architecture: Automated planning for ...*. https://www.sciencedirect.com/science/article/pii/S0167642323000606
8. *A survey of software refactoring | IEEE Journals & Magazine ...*. https://ieeexplore.ieee.org/document/1265817
9. *Extract Class - Refactoring.Guru*. https://refactoring.guru/extract-class
10. *Exploring and Analyzing Software Architecture Refactoring in ...*. https://ieeexplore.ieee.org/document/11267057
11. *add_column does not modify table.columns? - Google Groups*. http://groups.google.com/g/sqlalchemy-alembic/c/vrofUOaxvh0/m/gTa8GNMbjiUJ
12. *rollback - Liquibase*. https://docs.liquibase.com/secure/reference-guide-5-1-1/init-update-and-rollback-commands/rollback
13. *rollback - Liquibase Docs*. http://docs.liquibase.com/commands/rollback/rollback.html
14. *Migrations - Redgate Flyway - Product Documentation*. https://documentation.red-gate.com/fd/migrations-271585107.html
15. *Senior Database Administrator @ OCTAGOS HEALTH, INC.*. http://tealhq.com/job/senior-database-administrator_7ea1a8d5f374f011f558c70ec5aea71e17565
16. *The PARA Method: The Simple System for Organizing Your ...*. https://fortelabs.com/blog/para/
17. *PARA Method Template for Notion (Building a Second Brain)*. http://thomasjfrank.com/templates/para-method-template-for-notion
18. *Sayani Dutta*. https://linkedin.com/in/sayaniiiiiii
19. *Canon Protocol*. http://github.com/canon-protocol
20. *Medallion Architecture for Data Engineering projects*. http://github.com/somrajroy/medallion
21. *510(k) Premarket Notification - FDA*. http://accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=k232393
22. *GitHub - Z3Prover/z3: The Z3 Theorem Prover · GitHub*. https://github.com/Z3Prover/z3
23. *Z3® Waterline Purification Straw Box of 2*. http://shop.benco.com/Product/5455-045/z3-waterline-purification-straw-box-of-2
24. *Combining Objectives | Online Z3 Guide - GitHub Pages*. https://microsoft.github.io/z3guide/docs/optimization/combiningobjectives/
25. *Solomonoff's theory of inductive inference - Wikipedia*. https://en.wikipedia.org/wiki/Solomonoff%27s_theory_of_inductive_inference
26. *Bayesian information criterion - Wikipedia*. https://en.wikipedia.org/wiki/Bayesian_information_criterion
27. [[PDF] Understanding AIC and BIC in Model Selection | Multimodel Inference](http://sites.warnercnr.colostate.edu/wp-content/uploads/sites/73/2017/05/Burnham-and-Anderson-2004-SMR.pdf)
28. *Does Algorithmic Probability Solve the Problem of Induction?*. https://www.raysolomonoff.com/publications/isis96.pdf
29. *On the criteria to be used in decomposing systems into ...*. https://dl.acm.org/doi/10.1145/361598.361623
30. *Software Architecture in Practice - Len Bass, Paul Clements ...*. https://books.google.com/books/about/Software_Architecture_in_Practice.html?id=qNnPEAAAQBAJ
31. *Elementos de software orientado a objetos reutilizable*. http://profeuttec.yolasite.com/resources/Patrones%20de%20dise%C3%B1o%20-%20Erich%20Gamma.pdf
32. *Design Patterns: Elements of Reusable Object-Oriented Software*. https://www.pearson.com/en-us/subject-catalog/p/design-patterns-elements-of-reusable-object-oriented-software/P200000009480/9780321700698
33. *On the Criteria to be Used in Decomposing Systems into Modules*. https://link.springer.com/content/pdf/10.1007/978-3-642-59412-0_25.pdf
34. *Normalization in SQL (1NF - 5NF): A Beginner's Guide*. http://datacamp.com/tutorial/normalization-in-sql
35. *Ontology evolution as reconfiguration-design problem solving*. https://dl.acm.org/doi/10.1145/945645.945669
36. *Database Normalization: 1NF, 2NF, 3NF & BCNF Examples*. https://www.digitalocean.com/community/tutorials/database-normalization
37. *A Component-Based Framework For Ontology Evolution*. https://ceur-ws.org/Vol-71/Klein.pdf
38. *Development and production | Prisma Documentation*. http://prisma.io/docs/orm/prisma-migrate/workflows/development-and-production
39. *Migration Operations | Django documentation*. https://docs.djangoproject.com/en/6.0/ref/migration-operations/
40. *Generating down migrations | Prisma Documentation*. https://www.prisma.io/docs/orm/prisma-migrate/workflows/generating-down-migrations
41. *Schema migrations with Prisma and Neon - Neon Docs*. http://neon.com/docs/guides/prisma-migrations
42. *Django migrations RunPython reverse function - Stack Overflow*. https://stackoverflow.com/questions/73839299/django-migrations-runpython-reverse-function
43. *rollback - Liquibase*. https://docs.liquibase.com/commands/rollback/rollback.html
44. *Software Engineering Institute - Carnegie Mellon University*. http://sei.cmu.edu/
45. *Design Patterns: Elements of Reusable Object-Oriented Software*. https://www.pearson.com/en-au/subject-catalog/p/design-patterns-elements-of-reusable-object-oriented-software/P200000009480/9780321700698
46. *Design Patterns Elements of Reusable Object-Oriented Software*. http://javier8a.com/itc/bd1/articulo.pdf
47. *Parnas on Modularity | mateuszmarczak*. https://mateuszmarczak.com/blog/2025/10/03/parnas-modularity.html
48. *SEI Quality Model*. https://quality.arc42.org/articles/sei-quality-model
49. *How does L1 and L2 regularization prevent overfitting ...*. https://www.geeksforgeeks.org/machine-learning/how-does-l1-and-l2-regularization-prevent-overfitting/
50. *A Simple Way to Prevent Neural Networks from Overfitting*. http://jmlr.org/papers/v15/srivastava14a.html
51. *LogisticRegression — scikit-learn 1.8.0 documentation*. https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html
52. *Regularization Techniques: L1, L2, Dropout (ML context)*. https://www.sanfoundry.com/regularization-techniques-l1-l2-dropout/
53. *Dropout: A Simple Way to Prevent Neural Networks from Over tting*. https://www.cs.toronto.edu/~rsalakhu/papers/srivastava14a.pdf
54. *Z3: Optimize Class Reference - GitHub Pages*. https://z3prover.github.io/api/html/classz3py_1_1_optimize.html
55. *About Z3*. http://z3controls.com/about.php
56. *Soft Constraints | Online Z3 Guide - GitHub Pages*. https://microsoft.github.io/z3guide/docs/optimization/softconstraints/
57. *Z3: optimize Class Reference - GitHub Pages*. https://z3prover.github.io/api/html/classz3_1_1optimize.html
58. *z3py - z3 optimize and soft constraints - Stack Overflow*. https://stackoverflow.com/questions/77742069/z3-optimize-and-soft-constraints
59. *Operation Reference — Alembic 1.18.4 documentation*. https://alembic.sqlalchemy.org/en/latest/ops.html
60. *Microsoft Word - WPM$2031.doc - CEUR-WS.org*. https://ceur-ws.org/Vol-62/EON2002_Stojanovic.pdf
61. *Ontology Evolution: Not the Same as Schema Evolution - Springer*. https://link.springer.com/article/10.1007/s10115-003-0137-2
62. *mv(1) - Linux manual page*. http://man7.org/linux/man-pages/man1/mv.1.html
63. *Git - git-mv Documentation*. https://git-scm.com/docs/git-mv
64. *What is Medallion Architecture? - Databricks*. https://www.databricks.com/blog/what-is-medallion-architecture
65. *Databricks – AI Adoption*. http://dufrain.co.uk/partnerships/our-databricks-business/databricks-ai-adoption
66. *Denormalization in Databases: When and How to Use It*. https://www.datacamp.com/tutorial/denormalization
67. *Learning The Zettelkasten Method is Easy, Actually*. https://noahvnct.substack.com/p/learning-the-zettelkasten-method
68. *Organize Your Second Brain: How to Use the PARA Method*. http://web-highlights.com/blog/master-your-second-brain-part-1-how-to-use-the-para-method
69. *Types of Notes - PKM Zettelkasten*. https://zk.zettel.page/types-of-notes
70. *A No-Nonsense Guide to the PARA Method - Medium*. http://medium.com/practice-in-public/mastering-the-para-method-and-how-to-take-it-to-new-heights-d48afa1d13b0
71. *First normal form*. http://en.wikipedia.org/wiki/First_normal_form
72. *What is database normalization? - IBM*. https://www.ibm.com/think/topics/database-normalization
73. [Data Normalization: The Complete Guide With Examples [2026]](http://cleanlist.ai/blog/2026-04-12-data-normalization-complete-guide)
74. *Category:Database normalization*. http://en.wikipedia.org/wiki/Category%3ADatabase_normalization
75. *Software Consulting Services | AI, DevSecOps, Quality | Coveros*. http://coveros.com/services/agile-devops-transformation
76. *On the criteria to be used in decomposing systems into modules*. https://prl.khoury.northeastern.edu/img/p-tr-1971.pdf
77. *Software architecture analysis method — Grokipedia*. https://grokipedia.com/page/software_architecture_analysis_method
78. *Ontology-Driven GraphRAG: A Framework for Zero-Noise Knowledge Extraction | by Akash Goyal | Medium*. http://medium.com/%40aiwithakashgoyal/beyond-simple-extraction-how-production-grade-ontologies-transform-graphrag-from-prototype-to-333742fa41a6
79. *Ontology Evolution: Not the Same as Schema Evolution*. https://www.researchgate.net/profile/Michel-Klein/publication/248289911_Ontology_Evolution_Not_the_Same_as_Schema_Evolution/links/00b7d52272abdccdf9000000/Ontology-Evolution-Not-the-Same-as-Schema-Evolution.pdf
80. *LLM-empowered knowledge graph construction: A survey - arXiv*. http://arxiv.org/html/2510.20345v1
