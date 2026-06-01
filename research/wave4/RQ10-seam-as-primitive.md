# RQ10 — Seam as Primitive, Constraint, or Theorem?

**Thread:** A* Wave 4, RQ10-seam-as-primitive
**Source policy:** post-2005 architecture and capability literature, with canonical pre-2005 anchors (Parnas 1972, Bell-LaPadula 1973, Biba 1977, Goguen-Meseguer 1982, Lampson 1974) treated as foundational.
**Question:** Should the v0.1 two-layer seam invariants (`tenant_cannot_mutate_engine_state`, `engine_cannot_read_tenant_secrets`) live as (a) new primitive ops `DECLARE_LAYER` + `BIND_SEAM`, (b) a new integrity constraint IC4, or (c) derivable corollaries of IC3 (folder-as-contract) + the existing 9 ops?
**Method:** Claude Code native deep search (WebSearch + WebFetch). No Parallel.ai, no Anthropic API.
**Date:** 2026-05-24.

---

## Executive Summary

The recommendation is **placement (c) with a small, surgical IC3 reinforcement**: the seam invariants are derivable from IC3 once two facts are added to the manifest schema (a `layer` enum field and a `secret_classes` array), but the derivation requires one additional axiom that does not follow from IC3 alone — an asymmetric flow rule mapping `layer` labels to allowed write-direction and read-direction. The cleanest place to put that axiom is **as a clarifying clause in IC3, not as a new IC4 and not as new primitives**. No new ops are needed. The 9-op set already covers declaration (`UPDATE_MANIFEST` writes the `layer` field) and enforcement (the validator and QA agent read it). IC4 is rejected on minimality grounds (Occam): every observable seam-violation behaviour is a folder-contract violation in disguise, and inflating ICs to encode each new boundary class (dev/prod, public/private, human/machine, billable/non-billable) leads to constraint sprawl. The primitive-op placement is rejected because primitives in A* are state-transformation verbs over architecture; layer and seam are state-of-the-folder *properties*, not verbs. The strongest evidence for (c) is the convergence of three independent literatures (Parnas information hiding, hexagonal/onion/clean architecture, capability ocap) on a single pattern: layer membership is a declared property of a module; the asymmetric flow rule is a derived check; enforcement is mechanical (ArchUnit, Structurizr, NDepend for layers; SES/seL4 capability checks for the asymmetric flow). The strongest counter-evidence is the Bell-LaPadula / Biba tradition treating the asymmetric flow rule as a first-class axiom of the protection model rather than a consequence of labels; under that reading, IC4 is the more honest placement. The memo resolves this counter-evidence by noting that BLP/Biba treat *labels themselves* as primitive (security lattice elements assigned by a trusted authority); in A* the analogous primitive is the manifest, so the lattice element is the `layer` field of the manifest, and IC3 already governs manifest consistency. Therefore the BLP/Biba flow rules become *theorems* under IC3 once `layer` is in scope.

---

## Part A — Literature Survey

### A.1 Layer separation as a first-class architectural concept (Task 1)

Parnas's 1972 paper *On the Criteria to Be Used in Decomposing Systems into Modules* is the foundational text. Parnas argued that modules should be designed around **information hiding**: each module hides a design decision likely to change, and other modules cannot depend on the hidden decision [1]. The crucial observation for RQ10 is that Parnas's modules are defined by what they *hide*, not by what they *do*, and the "uses" relation between modules is asymmetric and declared, not inferred from code. This maps directly onto the A* seam: Layer A engine hides tenant identity from itself (it cannot read tenant secrets); Layer B tenant hides engine internals from itself (it cannot mutate engine state). The "uses" relation is asymmetric: tenant uses engine, engine does not use any particular tenant.

Bass, Clements, and Kazman in the *Software Architecture in Practice* tradition (3rd ed., 2012, and the SEI ATAM body of work) generalize Parnas's idea into **architectural views** and **layered styles** [2]. A layered style requires (i) a strict partition of components into layers, (ii) a dependency rule that constrains which layers may call which, (iii) tooling to enforce the rule. SEI's architecture-evaluation method is explicit that layer violations are quality-attribute risks, and that the layer declaration must be *part of the architecture document* rather than recovered from the source.

Alistair Cockburn's **hexagonal architecture** (ports and adapters) makes the asymmetry explicit at the boundary [3]. The core hexagon (domain) is surrounded by adapters; ports are interfaces *declared by the domain* that adapters must implement. The dependency rule: all dependencies point inward; the outside knows about the inside, the inside knows nothing about the outside [3]. This is the **exact shape** of the A* seam: the engine (Layer A) is the inside hexagon; tenant code (Layer B) is the adapter ring; ports are the engine's declared APIs; the seam invariants are the dependency rule.

Jeffrey Palermo's **onion architecture** (2008) restates the same rule in concentric-layer form [4]: "all code can depend on layers more central, but code cannot depend on layers further out from the core." Robert Martin's **clean architecture** (2012) makes the dependency rule global and explicit [5]: "source code dependencies can only point inwards. Nothing in an inner circle can know anything at all about something in an outer circle." All three patterns converge on a single property: **layer membership is declared per-component; the dependency rule is a derived check.** None of them introduces "layer" as a separate axiom outside the module declaration; they treat layer as a property of the module and the directional rule as a consequence of layer labels.

**Enforcement tooling** confirms this. ArchUnit, the canonical Java architecture-test library, expresses layer rules as `layeredArchitecture()` declarations where you (i) name layers by package pattern, (ii) declare allowed access [6]. Layer membership is therefore a derived attribute of a class (from its package), and the rule is checked against the model graph — the same shape as the A* QA agent's `seam.py`. Structurizr (Simon Brown) takes the same approach for C4 diagrams. NDepend uses CQLinq queries over the assembly graph. All three treat layer as **declared once, enforced everywhere** — exactly placement (c) with manifest-as-declaration.

**Soft vs hard layers.** The literature distinguishes a *soft* layer (convention, enforced by code review) from a *hard* layer (compiler/loader/runtime enforces) [2,3,5]. Parnas's modules in System/360 era were soft; Cockburn's hexagons in Java are soft (the JVM does not prevent cross-layer calls); seL4's capabilities are hard (the kernel refuses the call). A* IC3 manifests with CI validation are *hard*-soft: the validator blocks merge, which is enforcement at the workflow boundary rather than runtime. This positioning matters for placement: a hard runtime axiom would justify a new IC; a build-time check over declared metadata is the natural reading of IC3.

### A.2 Multi-tenant isolation: code-layer seam vs data-row seam (Task 2)

The multi-tenant SaaS literature (Krebs, Momm, Kounev) identifies three isolation axes: **performance**, **data**, and **code** [7]. Most of the operational SaaS literature focuses on data isolation (shared schema with `tenant_id`, schema-per-tenant, database-per-tenant). The Krebs/Momm/Kounev taxonomy notes that **code isolation** — the property that engine code is identical across tenants and tenant code does not modify engine code — is a distinct dimension that most multi-tenant systems achieve by **deployment topology** (one engine binary, many tenant configs) rather than by formal contract [7]. The A* seam is the formal-contract version of this property at the repository level.

**Kubernetes** uses **namespaces** as the tenant boundary, with RBAC roles scoped to a namespace as the access-control mechanism [8]. The Kubernetes multi-tenancy guide is explicit that **namespace boundaries are not security boundaries by default**: pods in different namespaces can communicate freely unless explicit NetworkPolicies are added [8]. This is the operational counterpart of A* IC3: declaring the boundary in the manifest is necessary but not sufficient; the seam invariants are the analytic checks that turn the declaration into an enforced contract.

**AWS Organizations and Service Control Policies (SCPs)** push the boundary up the hierarchy: SCPs are declared at organization unit (OU) level and define what *any* IAM principal in member accounts may do [9]. The SCP itself is a *declared policy*, not a new kind of resource. This maps cleanly to placement (c): the seam contract is a declared field on the manifest, not a new resource class.

**Site isolation in Chrome** (Reis et al., USENIX Security 2019) [10] is the strongest engineering evidence that the boundary must be (i) declared (one site per renderer process), (ii) mechanically enforced (filter cross-site data at the renderer boundary), (iii) defended against side-channels (Spectre). Reis et al. did not introduce a new web-security axiom; they made the existing same-origin policy *mechanically enforceable* by binding it to an OS process boundary. Analogously, A* IC3 + the seam invariants do not introduce a new architectural axiom; they bind the existing folder-contract to the layer-membership field of the manifest.

**Bottom line for Task 2:** the multi-tenant literature treats the engine/tenant boundary as a property of the *deployment topology* (namespaces, processes, accounts) and the enforcement as a *policy-on-declaration*. In A*, the deployment topology is the folder hierarchy; the declaration is the manifest; the enforcement is IC3-driven validation. Placement (c) is the literature-aligned choice.

### A.3 Capability security and the asymmetric flow rule (Task 3)

The seam invariants are precisely the shape of a **read/write asymmetry across a labelled boundary**. The classical models:

**Lampson's protection matrix** (1971/1974) [11] is the abstract baseline: rows are subjects (domains), columns are objects (resources), cells are right-sets `{r, w, x, o}`. The access rule is per-cell: a subject may perform operation `op` on object `o` iff `op ∈ matrix[subj, o]`. Layered systems are encoded by *labelling* subjects and objects and reading rights from the labels.

**Bell-LaPadula (BLP)** is the canonical confidentiality model [12]. Subjects and objects carry **security labels** from a lattice (e.g., `unclassified < confidential < secret < top_secret`). Two axioms:

- **Simple Security (no-read-up):** a subject at level `L` may not read an object at level `L' > L`.
- **Star (*) Property (no-write-down):** a subject at level `L` may not write to an object at level `L' < L`.

The intent is confidentiality: information flows up the lattice, never down. In the A* seam, the **engine cannot read tenant secrets** invariant is a BLP-style confidentiality cut: tenant secrets sit at a "more confidential" level than engine, and the engine (lower confidentiality) must not read them. The directional read is `engine ↛ read ← tenant_secret`.

**Biba (1977)** is the dual integrity model [13]. Labels carry **integrity levels** (e.g., `high_integrity > low_integrity`). Two axioms:

- **Simple Integrity (no-read-down):** a subject at integrity `I` may not read an object at integrity `I' < I`.
- **Integrity * Property (no-write-up):** a subject at integrity `I` may not write to an object at integrity `I' > I`.

The intent is integrity: dirty inputs cannot corrupt clean state. In the A* seam, **tenant cannot mutate engine state** is a Biba-style no-write-up: tenant code (lower integrity, fast-changing) cannot write to engine state (high integrity, slow-changing). The directional write is `tenant ↛ write → engine`.

**The clean mapping** of the two seam invariants:

```
A* seam invariant                          | classical model | rule
-------------------------------------------|------------------|---------------------------
tenant_cannot_mutate_engine_state         | Biba             | no-write-up (* property)
engine_cannot_read_tenant_secrets         | Bell-LaPadula    | no-read-up (simple security)
```

Both invariants share the lattice shape `{engine, tenant, shared}` with a partial order:

- **For integrity (Biba):** `engine > tenant` (engine is more trusted; tenant must not write up).
- **For confidentiality (BLP):** `tenant_secret > engine` (tenant secrets are more confidential; engine must not read up).

Note: the partial orders are *different* for the two invariants. Engine is high-integrity *and* low-confidentiality (from the tenant's secrets' perspective). This is exactly the standard combined BLP+Biba reading: one lattice for confidentiality, one for integrity, both layered over the same subjects/objects.

**Goguen-Meseguer noninterference** (1982) [14] gives the formal semantics that subsumes both: a system has the noninterference property iff a high-level subject's input has no effect on a low-level subject's observable output. In A* terms: tenant transitions should not affect engine state (Biba no-write-up); tenant secret state should not affect engine observable behaviour (BLP no-read-up). Goguen-Meseguer treats the security policy as *a function* mapping subjects to allowed-input sets; the policy itself is a declared object, not a kernel axiom. This is structurally identical to placement (c): the manifest declares the layer; IC3 governs the manifest; the noninterference property follows.

**Object capabilities (ocap, Mark Miller, SES)** [15] take the dual approach: instead of labelling subjects and objects and checking labels at access time, ocap removes access by default (no ambient authority) and grants access by passing unforgeable references. The **principle of least authority (POLA)** [16] is the design rule. KeyKOS, EROS, and seL4 implement this in a kernel [17,18]; SES does it in JavaScript [15]. The relevance to RQ10: ocap *does not need an IC4* because the rule is enforced by the structure of references, not by a separate policy axiom. By analogy, A* does not need an IC4 if the rule is enforced by the structure of the manifest (which folder declares which layer) plus the existing IC3 governance.

**Bottom line for Task 3:** the seam invariants map cleanly into Biba (no-write-up) + BLP (no-read-up) on a `{engine, tenant, shared}` lattice with the two partial orders above. The mapping is mathematically sound. The placement question is whether the lattice and the flow rules are **primitive axioms** (the BLP/Biba kernel reading) or **declared metadata + derived checks** (the ocap/Goguen-Meseguer reading). A* IC3 already treats manifests as the unit of declared metadata, so the ocap/GM reading is the natural fit.

### A.4 Core/extension schemas and the protection mechanism (Task 4)

Four canonical schema-evolution patterns where a core protects itself from an extension and vice versa:

**WordPress core vs plugins** [19]. WordPress separates files into `wp-includes/` and `wp-admin/` (core) vs `wp-content/plugins/` and `wp-content/themes/` (extension). The core exposes the **Plugin API** (added in WP 1.5): actions and filters that plugins hook into. There is **no kernel-level enforcement** — a malicious plugin can write core files. The boundary is *convention enforced by deployment* (the plugin must live in `wp-content/`) and **WordPress core itself ships a checksum check** to detect modified core files. The seam mechanism is therefore (i) path-based declaration of layer (folder hierarchy), (ii) a manifest-style declaration of plugin metadata in the plugin's header comment, (iii) an out-of-band integrity check on core files. This is placement (c) almost verbatim, including the limitation: WP cannot prevent the violation, only detect it. A* with CI validation is in the same posture.

**Kubernetes CRD vs operator** [20,21]. CRDs declare the *schema* of a custom resource; operators implement the *control loop* that reconciles it. The separation is enforced by the Kubernetes API server: a CRD without a registered operator does nothing; an operator without a CRD has nothing to reconcile. The mechanism: **CRDs are declared metadata** (YAML); the operator is a separate deployment; the API server is the integrity boundary. Note that CRDs are deployable independently of cluster lifecycle, and operators are deployable independently of CRDs. The two layers evolve on separate cadences — the literature explicitly notes this is the whole point [20].

**PostgreSQL extensions** [22]. Extensions are packaged as `.control` files plus SQL/loadable shared libraries. The `.control` file is a **declared manifest** stating the extension's name, version, requires, schema, relocatable, etc. The PostgreSQL core enforces extension-installation rules (`CREATE EXTENSION` checks the control file) but **does not isolate extension code at runtime** — a `superuser` extension can do anything. The protection is **schema-level**: each extension can request its own schema, and tenant code can grant or revoke per-schema access. Again the pattern is *declared metadata + check-on-install*.

**Browser engine vs extension** (Chrome's site isolation) [10]. Each web site runs in a separate renderer process; extensions run in their own process with manifest-declared permissions (manifest.json). The boundary is **OS-process-enforced**. The declaration is **manifest.json** (layer = `content_script`, `background`, `popup`; permissions = explicit list). The browser refuses to load a content script into a page if the manifest does not declare permission. This is the strongest form of the pattern — hard runtime enforcement of declared metadata.

**Pattern across all four:** core/extension separation is uniformly achieved by **(i) declared manifest stating extension/layer membership, (ii) host-side enforcement reading the manifest, (iii) optional integrity check on the core**. None of the four introduces a separate top-level invariant outside the manifest declaration. The mechanism varies (process, schema, file) but the **layer-as-manifest-field** pattern is universal.

---

## Part B — Formal Mapping into Biba + BLP

### B.1 The lattice

Let `Layer = {engine, tenant, shared}` be the set of layer labels. Define two partial orders:

**Integrity lattice (Biba):**

```
engine  >_I  shared  >_I  tenant
```

Reading: engine has the highest integrity (carefully reviewed, audited, multi-tenant-shared). Shared is intermediate (libraries, contracts). Tenant is lowest integrity (one-off, fast-changing). Biba's no-write-up: a subject at integrity `I` may not write up; in particular, a tenant transition may not write to engine state.

**Confidentiality lattice (BLP):**

```
tenant_secret  >_C  tenant_data  >_C  shared  >_C  engine
```

Reading: tenant secrets (`.env`, `secrets/`, `credentials/`) are the most confidential. Tenant data (leads, deliveries) are sensitive but lower. Shared and engine are non-confidential from the tenant's perspective. BLP's no-read-up: a subject at confidentiality `C` may not read up; in particular, an engine transition may not read a tenant secret.

### B.2 The two seam invariants as theorems of (Biba + BLP)

**Theorem 1 (tenant_cannot_mutate_engine_state).** For any transition `t` with `scope(t) = tenant` and `writes_paths(t) ∋ p`, if `owner(p) = engine`, then `t` is a Biba * Property violation.

*Proof.* By the integrity lattice, `tenant <_I engine`. Writing to a path owned by `engine` is writing to an object of integrity `engine`. A subject of integrity `tenant` writing to an object of higher integrity is forbidden by Biba's * Property. QED.

**Theorem 2 (engine_cannot_read_tenant_secrets).** For any transition `t` with `scope(t) = engine` and `reads_paths(t) ∋ p`, if `secret_class(p) = tenant_secret`, then `t` is a BLP Simple Security violation.

*Proof.* By the confidentiality lattice, `engine <_C tenant_secret`. Reading a path of class `tenant_secret` is reading an object of confidentiality `tenant_secret`. A subject of confidentiality `engine` reading an object of higher confidentiality is forbidden by BLP's Simple Security Property. QED.

### B.3 Soundness conditions for the mapping

The two theorems are sound iff:

1. **Every path is labelled.** Every filesystem path that participates in a transition has a determined `owner` (Biba label) and a determined `secret_class` (BLP label). In the A* impl today, `owner` is computed by prefix-match against `scope.owns_paths`, and `secret_class` is computed by substring match against `DEFAULT_SECRET_PATTERNS`. Both are total functions once defaults are set.
2. **Every transition is labelled.** Every transition has a `scope` field. In v0.1.1 the field is optional (back-compat). For the mapping to be sound under IC3, the manifest schema must require `scope` on every declared transition (or default to `shared` with a warning).
3. **The labels are declared in the manifest.** Both `scope.owns_paths` and the secret-class predicate are declared, not inferred from runtime behaviour. This is the IC3 hook.

Conditions 1 and 2 are already met in the QA agent's analytic checker. Condition 3 requires that the manifest schema gain a `layer` field (currently it has `scope` as a sentence, not a layer enum) and optionally a `secret_classes` array.

---

## Part C — IC3-Derivation Sketch

### C.1 What IC3 says today

A_STAR_v0.md §3, IC3 (revised in RQ5):

> Every stable folder that functions as a navigation, ownership, lifecycle, or execution boundary declares a manifest containing: scope, exclusions, allowed artifact types, owner, lifecycle status, required metadata, outbound relations, and review cadence.

The implementation (`impl/a_star/manifest/schema.py`) enforces this via JSON Schema: each manifest must have `scope` (string), `exclusions`, `allowed_artifact_types`, `owner`, `lifecycle_status`, `required_metadata`, `outbound_relations`, `review_cadence`, and `retention`. No `layer` field, no `secret_classes`.

### C.2 What additional axiom is needed for the seam invariants to follow

The seam invariants do **not** follow from IC3 as currently written. IC3 requires manifest consistency; it does not say anything about asymmetric flow between layers.

For Theorems 1 and 2 to follow from IC3, we need **one** new axiom (the "asymmetric flow axiom"):

> **Asymmetric flow axiom.** If a folder's manifest declares `layer = L`, and a transition originating in the folder mutates or reads a path declared by another folder's manifest as `layer = L'`, then the transition is valid iff the integrity and confidentiality lattices over `(L, L')` permit it.

This axiom is *external* to IC3 today. The question is where it best lives.

**Option (c1): Extend IC3 with the asymmetric flow axiom.** Add a clarifying sentence to IC3 stating that manifest consistency includes asymmetric flow when layer labels are present. Minimal: 2 sentences. No new IC, no new primitive op. The schema gains a `layer` enum and a `secret_classes` array. The validator gains the analytic check (which already exists in `qa-agent/qa_agent/mbt/seam.py` and can be ported to `impl/a_star/manifest/validator.py`).

**Option (c2): Pure derivation, no axiom change.** Argue that the asymmetric flow rule is *already* implicit in IC3's "outbound_relations" mechanism. If a folder declares an outbound relation `depends_on: engine`, then the dependency direction is engine ← tenant; the inverse direction (engine writing to tenant or engine reading tenant secrets) is *not* declared and is therefore forbidden by IC3's "manifest is the contract" principle. This is a stronger claim and probably overreach: IC3 today says manifests must be *consistent*, not *complete*. The asymmetric flow rule needs the *complete* reading.

**Verdict:** (c1) is honest, (c2) is wishful. The recommendation is (c1) — fold the asymmetric flow axiom into IC3 as a clarifying clause, expand the schema, no new IC, no new primitive op.

### C.3 Why this is not IC4

IC1 (canonicality), IC2 (retention), IC3 (manifest consistency) are each about a *different invariant of the architecture state*. IC1 governs source-of-truth uniqueness. IC2 governs lifecycle/retention. IC3 governs the contract between a folder and its consumers. The seam invariants are *not* about a fourth invariant of state; they are about the contract a folder publishes about its layer membership. That is IC3 with one more field, not a separate IC.

Inflating to IC4 invites IC5 for dev/prod, IC6 for public/private, IC7 for human/machine, IC8 for billable/non-billable. Each is the same shape (asymmetric flow over a labelled lattice). Folding them all into IC3 keeps the constraint count constant as the label space grows.

### C.4 Why this is not new primitive ops

Primitives in A* are state-transformation verbs (CREATE_FOLDER, MOVE_ARTIFACT, UPDATE_MANIFEST, ...). They are emitted by the solver as a transaction. `DECLARE_LAYER` and `BIND_SEAM` are not verbs — they are *property declarations* about a folder's manifest. Declaring `layer = engine` is just `UPDATE_MANIFEST({layer: engine})`. Binding a seam is just *checking* the layer label on read/write — a validator concern, not a primitive.

Adding `DECLARE_LAYER` would force every Layer-A folder to emit a primitive to declare its layer; this is exactly the kind of solver fire-hose that v0.1.1's stub-manifest tool was designed to avoid. UPDATE_MANIFEST already covers it.

---

## Part D — Three-Placement Scoring Matrix (Task 6)

Each criterion scored 1-5 (5 = best for that placement).

| Criterion | (a) DECLARE_LAYER + BIND_SEAM primitives | (b) IC4 new constraint | (c) IC3 clarification + schema fields |
|---|---|---|---|
| **Minimality (Occam)** | 1. Adds 2 new ops to the 9-op set (+22%). Each future seam type adds more. | 2. Adds 1 new top-level IC. Each future label class invites another IC. | **5. No new IC, no new ops. One clarification sentence + 1-2 schema fields.** |
| **Spec stability** | 2. Primitives are part of the solver contract; adding them changes Z3 model size and the emission format. Each new seam type breaks emission compat. | 3. ICs are public spec surface; adding IC4 is a v0.2 breaking change for existing manifests (must add `layer`). New label classes need new ICs. | **5. Schema gains optional fields; IC3 wording adds a conditional clause. Back-compat by default (`layer` defaults to `shared`).** |
| **Implementation cost** | 1. Two new ops with pre/post conditions, inverses, per-axis C_core deltas, K-class usage notes. Plus solver wiring. ~300 LOC of new spec + impl. | 3. One new IC; validator gains a new check method; QA invariants port from seam.py. ~150 LOC. | **5. Schema gains `layer` enum + `secret_classes`. Validator gains 1 check method that ports from `qa-agent/qa_agent/mbt/seam.py` (~50 LOC already written).** |
| **Composability with existing 9 ops** | 1. Conflict: `DECLARE_LAYER` overlaps with `UPDATE_MANIFEST`. Macros would be needed to avoid duplicate declarations. | 4. Orthogonal to ops; runs as validator. | **5. Orthogonal; runs as validator; `UPDATE_MANIFEST` already writes the field.** |
| **Generalization to other seams** (dev/prod, public/private, human/machine, billable/non-billable) | 1. Each new seam needs its own primitive pair. Op count explodes. | 2. Each seam invites a new IC. IC count grows linearly with label classes. | **5. Each new seam adds one more `layer`-style enum field to the schema and one more check-clause. IC3 wording does not change.** |
| **Mirrors literature** | 2. No analogue in capability or layered-architecture literature. | 3. Matches the BLP/Biba "kernel axiom" reading. | **5. Matches the ocap, hexagonal/onion/clean, Goguen-Meseguer, ArchUnit, Kubernetes CRD, Chrome site-isolation, WordPress core/plugin, Postgres extension reading: declared-metadata + check-on-validation.** |
| **Total** | **8 / 35** | **17 / 35** | **30 / 35** |

Placement (c) wins on every criterion. The closest competitor is (b) IC4, and only because the BLP/Biba kernel-axiom reading is honest. The deciding factor is **generalization**: any future seam type (RQ10's Task 7 list) can be added under (c) without spec churn; under (b), each new seam invites a new IC.

---

## Part E — Generalization to Other Seams (Task 7)

The same machinery (layer enum + asymmetric flow check) handles all candidate seams:

| Seam | Layer enum | Integrity order | Confidentiality order | Check pattern |
|---|---|---|---|---|
| **engine/tenant** (v0.1) | `{engine, tenant, shared}` | `engine > shared > tenant` | `tenant_secret > tenant > shared > engine` | tenant ↛ write engine; engine ↛ read tenant_secret |
| **dev/prod** | `{prod, staging, dev}` | `prod > staging > dev` | `prod_data > staging_data > dev_data` | dev ↛ write prod; dev ↛ read prod_data |
| **public/private** | `{public, internal, private}` | n/a (use confidentiality) | `private > internal > public` | public_artifact ↛ derived_from private (BLP-style) |
| **human/machine-generated** | `{human, machine, hybrid}` | `human > machine` (provenance) | n/a | machine ↛ overwrite human (Biba-style, no-write-up to human-authoritative state) |
| **billable/non-billable** | `{billable, non_billable, shared}` | n/a | n/a (cost attribution, not flow) | billable transitions must declare cost-center; non_billable ↛ consume billable resources (resource-flow) |
| **PII/non-PII** (v0.1.1 RQ11b precursor) | `{pii, derived_pii, non_pii}` | n/a | `pii > derived_pii > non_pii` | non_pii ↛ derived_from pii without anonymisation step (BLP + sanitiser) |

The pattern holds: each seam is a `layer`-style enum plus an asymmetric-flow check. Some use the Biba integrity reading, some use the BLP confidentiality reading, some use both, and some (billable) use a non-flow asymmetry (resource attribution). All fit the same IC3-clarification + schema-field shape.

This generalization is the strongest reason to reject (b) IC4: under (b), v0.2 would need IC4 (engine/tenant), v0.3 might need IC5 (dev/prod), v0.4 IC6 (public/private), etc. The IC count would grow with the label-class count, which contradicts A*'s explicit "minimal complete constraint set" stance (3 ICs, frozen since v0).

---

## Part F — S(M, T, L) Reduction Sketch (Task 8)

v0 §8 establishes that `S(M, T)` is the routing special case of A*: `S(M, T) = argmax_M S = A*(I, L, K=routing, T)` when folder/naming/archival/persistence are fixed.

The question: does introducing a layer dimension `L_layer` (distinct from the lifecycle stage `L`) change the reduction?

**Claim:** `L_layer` is absorbed by `K` as a per-layer K-profile, not as a new free variable in S(M, T, L).

**Argument.** A layer label is a *partition of the architecture state* into engine-owned and tenant-owned regions. Within each region, the K-class applies: Layer A engine has its own `K_engine` (e.g., `engine-of-outbound-pipeline` under RQ9's lattice form, or `infrastructure-of-K` under the fixed-taxonomy form). Layer B tenant has its own `K_tenant` (e.g., `outbound-pipeline` for AgencyA). The routing decision (model selection) under `S(M, T)` is made *within a layer*; the model selected for a Layer A transition is constrained by `K_engine`, and the model selected for a Layer B transition is constrained by `K_tenant`.

Therefore the routing function generalizes to:

```
S(M, T, layer) = A*(I, L_lifecycle, K = K_routing × layer, T)
```

where `K_routing × layer` denotes the per-layer K-profile, not a new dimension. The formal reduction proven in RQ8 is unchanged: routing is still A* restricted to fixed structure, with the per-layer K being the only addition. The simplicity prior `H_simp` is now per-layer (since the layer determines which K applies).

**Corollary.** S does not need to be re-derived for v0.2; the existing reduction suffices once `K` is read as `(K_class, layer)`.

---

## Part G — Recommendation (Task 9)

### G.1 Verdict

**Adopt placement (c): IC3 clarification + schema fields. Reject (a) and (b).**

The seam invariants become theorems of an extended IC3. No new primitive ops. No new top-level integrity constraint. The manifest schema gains two fields. The validator gains one analytic check method that ports nearly verbatim from `qa-agent/qa_agent/mbt/seam.py`.

### G.2 Precise A_STAR_v0.md textual diff

The diff is **surgical**: 1 sentence added to §3 IC3, 2 manifest-schema fields documented inline, 1 mapping paragraph added at the end of §3, and a 4-line footnote in §9 noting that UPDATE_MANIFEST covers the layer-field declaration.

**§3 IC3 — change the wording.**

Replace the current IC3 paragraph (lines 63-65 of A_STAR_v0.md):

> **IC3 — Manifest Consistency (folder-as-contract, revised in RQ5).** Every stable folder that functions as a navigation, ownership, lifecycle, or execution boundary declares a manifest containing: scope, exclusions, allowed artifact types, owner, lifecycle status, required metadata, outbound relations, and review cadence. For agent-heavy systems (`T_agent_internal` high), manifests must be machine-readable (YAML/JSON + JSON Schema) and CI-validated. Cross-cutting meaning lives in facets/tags; relation-dense meaning lives in typed graph edges. The repository ontology is layered across folders + facets + tags + graphs + schemas + search.

With:

> **IC3 — Manifest Consistency (folder-as-contract, revised in RQ5; layer-aware in RQ10).** Every stable folder that functions as a navigation, ownership, lifecycle, or execution boundary declares a manifest containing: scope, exclusions, allowed artifact types, owner, lifecycle status, required metadata, outbound relations, review cadence, and **layer** (one of `{engine, tenant_<id>, shared}`; default `shared` for back-compat). Folders that hold or reference confidential data additionally declare **secret_classes** (an array of path-pattern → confidentiality-class mappings; default empty). For agent-heavy systems (`T_agent_internal` high), manifests must be machine-readable (YAML/JSON + JSON Schema) and CI-validated. Cross-cutting meaning lives in facets/tags; relation-dense meaning lives in typed graph edges. The repository ontology is layered across folders + facets + tags + graphs + schemas + search.
>
> **Asymmetric flow under IC3 (RQ10).** When two folders declare different layer labels, any operation that originates in folder `F` and reads or writes a path owned by folder `F'` is valid iff the (integrity, confidentiality) lattice over `(layer(F), layer(F'))` permits the direction. Concretely: (i) **integrity** orders layers as `engine > shared > tenant_<id>`, and a transition originating in a lower-integrity layer must not write to a path owned by a higher-integrity layer (Biba * Property); (ii) **confidentiality** orders secret-classes as `tenant_secret > tenant_data > shared > engine`, and a transition originating in a lower-confidentiality layer must not read a path of higher confidentiality class (Bell-LaPadula Simple Security). The two seam invariants `tenant_cannot_mutate_engine_state` and `engine_cannot_read_tenant_secrets` (v0.1 QA agent) are theorems of this clause. New seam types (dev/prod, public/private, human/machine-generated, billable/non-billable, PII/non-PII) are accommodated by extending the layer enum and the lattice, not by adding new ICs or new primitive ops.

**§9 Primitive Operations — add a 4-line footnote** after the 9-op list (after line 213 of A_STAR_v0.md):

> *Note (RQ10):* Layer declaration is a manifest field, not a primitive op. Setting or changing a folder's layer is `UPDATE_MANIFEST({layer: ...})`. Seam enforcement is a validator concern (IC3) and produces no emitted primitive. This keeps the 9-op set minimal as new seam types are added.

**§5 Project Class `K` — add a 2-line note** at the end of §5 (after line 116 of A_STAR_v0.md):

> **Layer interaction (RQ10):** `K` is per-layer. An engine layer (`layer = engine`) carries an engine-of-`K` profile; a tenant layer carries the tenant `K` profile. Routing under `S(M, T)` (§8) is per-layer; the formal reduction (RQ8) is unchanged once `K` is read as `(K_class, layer)`.

**No changes** to §1 (the function signature `A*(I, L, K, T) → (A, D)` is unchanged; `L` continues to denote lifecycle stage), §2 (C_core), §4 (Intent), §6 (Team), §7 (COP), §10 (archival), §11 (gaps), §12 (roadmap), §13 (limitations), §14 (references).

### G.3 Implementation impact

| Surface | Change | Effort |
|---|---|---|
| `impl/a_star/manifest/schema.py` | Add `layer` enum property; add `secret_classes` array property. No required-field change (both default). | ~20 LOC |
| `impl/a_star/manifest/validator.py` | Add `validate_asymmetric_flow(model)` method porting `qa-agent/qa_agent/mbt/seam.py` logic. | ~80 LOC |
| `impl/a_star/solver/model.py` | No change. Z3 model is unchanged; `layer` is a label, not a free variable. | 0 LOC |
| `impl/a_star/primitives/` | No change. 9 ops unchanged. | 0 LOC |
| Tests | Port `qa-agent` seam tests to A* unit tests; add 4 new IC3 tests (layer present, layer missing back-compat, Biba violation, BLP violation). | ~120 LOC |
| `qa-agent` | No change. The seam invariants remain enforced where they live today. The validator is *additionally* checking at A* validate-time, but does not displace the runtime QA check. | 0 LOC |

Total: ~220 LOC of impl + tests, no new primitive ops, one spec sentence + two schema fields. This is the *minimum-disturbance* change consistent with the literature.

---

## Part H — Falsifiers (Task 10)

The recommendation (placement c, IC3 clarification + 2 schema fields) is falsified if:

1. **A real seam-violation case in v0.2 cannot be classified by the (integrity, confidentiality) lattice.** Example falsifier: a tenant transition that needs to *read* engine state (allowed by Biba, allowed by BLP) but for a reason that should be denied — e.g., the engine state contains a "next-tenant secret" that this tenant must not see. This would mean the labels are too coarse and the lattice needs a third dimension. Likely fix: add a third label-axis (e.g., per-tenant scoping), not abandon (c).

2. **The validator's manifest-driven check produces false negatives because layer declarations drift from reality.** Example: a folder is renamed but its manifest's `owns_paths` is stale; a tenant transition writes to what *is now* an engine path but the manifest still labels it tenant. This is a known weakness of declaration-based contracts; capability ocap (KeyKOS, seL4) addresses it with kernel-level enforcement, which is not available in A*'s build-time setting. Fix is operational (CI check that every path is owned by exactly one manifest), not a placement change.

3. **A new seam type requires a flow rule that is not expressible on a lattice.** Example: billable/non-billable resource attribution is not a Biba or BLP rule; it is an *aggregation* constraint (every cost-incurring transition must declare a billable cost-center). If a future seam needs this, IC3 may need a third clause (resource-attribution) parallel to the asymmetric-flow clause. Still no new IC, but the IC3 wording would grow.

4. **The Z3 model needs to reason about layer.** If the solver needs to *optimize* over layer (e.g., decide whether a new folder is best placed as engine or tenant), then `layer` becomes a free variable in the COP, not just a declared label. This would push layer into the COP encoding and possibly require a primitive op `BIND_SEAM` after all. The current architecture (solver emits per-folder primitives; layer is declared per-folder) does not require this. Falsifier: a project where the optimal layer placement is non-obvious and must be solved.

5. **A multi-tenant engine serves N tenants, and the lattice becomes a partial order rather than a total order.** Then `engine > tenant_agencya` and `engine > tenant_brandb` are incomparable across tenants. The Biba/BLP reading still works (each pair is independently checked), but reasoning about cross-tenant flows requires additional structure. Likely fix: extend the lattice to `{engine, tenant_<id>...}` with explicit incomparability, not abandon (c).

6. **The literature converges on a new boundary-enforcement primitive (e.g., a typed-interface check that the solver must emit).** If, e.g., a future architecture-test framework standardizes a primitive emission for layer boundaries, A* may want to match. No current sign of this; ArchUnit, NDepend, Structurizr all run as validators.

7. **The asymmetric-flow axiom contradicts an existing IC3 check.** Unlikely (the axiom is purely additive), but a falsifier: an existing v0.1 manifest passes IC3 today but fails the asymmetric-flow check; this would mean the new axiom rejects previously-valid architectures. Mitigated by the `layer` default of `shared` and back-compat.

---

## Part I — Closing

The seam invariants are not a new architectural axiom; they are the asymmetric-flow corollary of layer-membership declared on the manifest. Three independent literatures (Parnas/hexagonal/onion/clean architecture, BLP/Biba/Goguen-Meseguer, ocap/SES/seL4) converge on this reading. The Kubernetes CRD/operator, WordPress core/plugin, Postgres extension, and Chrome site-isolation engineering patterns all instantiate the same shape: declared metadata + check-on-validation. A* IC3 is already the declared-metadata mechanism for folder contracts; folding the asymmetric-flow axiom into IC3 keeps the constraint count at 3 and the primitive count at 9, while making the seam invariants first-class theorems of the spec. The change is one IC3 sentence, one §5 note, one §9 footnote, two schema fields, and ~220 LOC of validator + tests. v0.2 ships with seam-aware IC3.

---

## Bibliography

[1] Parnas, D. L. (1972). "On the Criteria To Be Used in Decomposing Systems into Modules." *Communications of the ACM* 15(12). https://dl.acm.org/doi/10.1145/361598.361623 ; full text PDF http://sunnyday.mit.edu/16.355/parnas-criteria.html ; CMU TR predecessor https://prl.khoury.northeastern.edu/img/p-tr-1971.pdf

[2] Bass, L., Clements, P., Kazman, R. (2012). *Software Architecture in Practice*, 3rd ed., Addison-Wesley. SEI ATAM body of work: https://www.sei.cmu.edu/architecture/

[3] Cockburn, A. "Hexagonal architecture" (2005, revised through 2026). https://alistair.cockburn.us/hexagonal-architecture ; Wikipedia overview https://en.wikipedia.org/wiki/Hexagonal_architecture_(software) ; AWS prescriptive guide https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/hexagonal-architecture.html

[4] Palermo, J. (2008). "The Onion Architecture: Part 1." https://jeffreypalermo.com/2008/07/the-onion-architecture-part-1/

[5] Martin, R. C. (2012). "The Clean Architecture." Clean Coder Blog. https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html

[6] ArchUnit User Guide and project. https://www.archunit.org/userguide/html/000_Index.html ; Examples: https://deepwiki.com/TNG/ArchUnit/5.3-examples-and-use-cases ; InfoQ overview https://www.infoq.com/news/2022/10/archunit/

[7] Krebs, R., Momm, C., Kounev, S. (2012). "Architectural Concerns in Multi-tenant SaaS Applications." *Proc. CLOSER*. https://www.semanticscholar.org/paper/Architectural-Concerns-in-Multi-tenant-SaaS-Krebs-Momm/71833696ace95643a1e1dba1afcdc7bb1090031d ; companion performance-isolation paper https://dl.acm.org/doi/10.1145/2405178.2405184 ; AWS SaaS tenant isolation strategies https://d1.awsstatic.com/whitepapers/saas-tenant-isolation-strategies.pdf

[8] Kubernetes multi-tenancy concept docs. https://kubernetes.io/docs/concepts/security/multi-tenancy/ ; Sysdig three boundaries https://www.sysdig.com/blog/multi-tenant-isolation-boundaries-kubernetes ; namespace boundaries are not security boundaries https://blog.amberwolf.com/blog/2025/september/kubernetes_namespace_boundaries/

[9] AWS Organizations Service Control Policies. https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html ; examples repo https://github.com/aws-samples/service-control-policy-examples

[10] Reis, C., Moshchuk, A., Oskov, N. (2019). "Site Isolation: Process Separation for Web Sites within the Browser." *USENIX Security 19*. https://www.usenix.org/conference/usenixsecurity19/presentation/reis ; PDF https://www.usenix.org/system/files/sec19-reis.pdf ; Chromium docs https://chromium.googlesource.com/chromium/src/+/main/docs/process_model_and_site_isolation.md

[11] Lampson, B. W. (1974). "Protection." *ACM Operating Systems Review* 8(1). https://cseweb.ucsd.edu/classes/fa01/cse221/papers/lampson-protection-osr74.pdf ; access-control matrix overview https://en.wikipedia.org/wiki/Access_control_matrix

[12] Bell, D. E., LaPadula, L. J. (1973-1976). MITRE Bell-LaPadula technical reports. Wikipedia summary with axioms: https://en.wikipedia.org/wiki/Bell%E2%80%93LaPadula_model ; ScienceDirect synthesis https://www.sciencedirect.com/topics/computer-science/lapadula-model

[13] Biba, K. J. (1977). "Integrity Considerations for Secure Computer Systems." MITRE Tech Report ESD-TR-76-372. Wikipedia summary https://en.wikipedia.org/wiki/Biba_Model ; ScienceDirect https://www.sciencedirect.com/topics/computer-science/biba-model ; comparison with BLP https://library.mosse-institute.com/articles/2022/05/the-biba-model-a-comparison-between-bell-lapadula/the-biba-model-a-comparison-between-bell-lapadula.html

[14] Goguen, J. A., Meseguer, J. (1982). "Security Policies and Security Models." *IEEE Symposium on Security and Privacy*. Wikipedia summary https://en.wikipedia.org/wiki/Non-interference_(security) ; SpringerLink chapter https://link.springer.com/doi/10.1007/978-1-4419-5906-5_874 ; Purdue lecture notes https://www.cs.purdue.edu/homes/ninghui/courses/526_Fall14/handouts/14_526_topic18.pdf

[15] Miller, M. S. et al. SES (Secure ECMAScript) and ocap in JavaScript. Agoric writeup: https://medium.com/agoric/ses-securing-javascript-in-the-real-world-4f309e6b66a6 ; Agoric blog https://agoric.com/blog/technology/ses-securing-javascript/ ; awesome-ocap https://github.com/dckc/awesome-ocap

[16] Principle of Least Authority (POLA) overview. https://www.lepide.com/blog/what-is-the-principle-of-least-privilege-polp/ ; capability-security application https://blog.monstuff.com/archives/000102.html ; Wikipedia PoLP https://en.wikipedia.org/wiki/Principle_of_least_privilege

[17] Shapiro, J. S. et al. EROS / KeyKOS lineage. EROS Wikipedia https://en.wikipedia.org/wiki/EROS_(microkernel) ; State Caching paper https://www.researchgate.net/publication/242370168_State_Caching_in_the_EROS_Kernel

[18] Elkaduwe, D., Klein, G., Elphinstone, K. "Verified Protection Model of the seL4 Microkernel." https://trustworthy.systems/publications/nicta_full_text/1474.pdf ; seL4 functional-correctness paper https://www.researchgate.net/publication/220420663_seL4_Formal_Verification_of_an_Operating-System_Kernel ; project page https://trustworthy.systems/projects/seL4/tech

[19] WordPress core vs plugins architecture. https://www.liquidweb.com/wordpress/development/architecture/ ; Make WordPress Core APIs handbook https://make.wordpress.org/core/handbook/best-practices/core-apis/ ; What is WordPress Core https://solidwp.com/blog/wordpress-core/

[20] Kubernetes Custom Resources concept doc. https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/ ; Operator pattern https://kubernetes.io/docs/concepts/extend-kubernetes/operator/

[21] Kubernetes Operator pattern in practice. https://iximiuz.com/en/posts/kubernetes-operator-pattern/ ; CRDs and reconciliation https://dev.to/naveens16/beyond-yaml-building-kubernetes-operators-with-crds-and-the-reconciliation-loop-524d

[22] PostgreSQL extension architecture. https://airbyte.com/data-engineering-resources/postgresql-extensions ; architecture overview https://deepwiki.com/postgres/postgres/1.1-architecture-overview ; extensions-vs-protocols essay https://materializedview.io/p/postgresql-extensions-or-protocols

[23] Conway's Law and the inverse / mirroring hypothesis. Wikipedia https://en.wikipedia.org/wiki/Conway's_law ; MacCormack/Baldwin/Rusnak mirroring hypothesis discussion https://lawsofsoftwareengineering.com/laws/conways-law/ ; inverse Conway maneuver https://learningloop.io/glossary/conways-law

[24] Object-capability model. Wikipedia https://en.wikipedia.org/wiki/Object-capability_model ; Grokipedia https://grokipedia.com/page/Object-capability_model ; capability-credentials directory https://decentralized-id.com/development/object-capabilities/

[25] Kubernetes RBAC and namespace isolation for multi-tenancy. https://oneuptime.com/blog/post/2026-01-19-kubernetes-rbac-multi-tenant-best-practices/view ; namespace isolation guide https://www.securview.com/ai-security-essentials/kubernetes-namespace-isolation

---

*RQ10 closed 2026-05-24. Recommendation: placement (c). v0.2 spec diff above is precise and applies cleanly against `A_STAR_v0.md` as of the 2026-05-21 freeze.*
