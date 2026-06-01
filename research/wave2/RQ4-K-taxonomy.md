# Constraint Profiles for Neural Project Architectures

## Executive Summary

- **K Should Classify Binding Constraints**: The strongest literature signal is that architecture methods classify drivers, views, quality attributes, lifecycles, and boundaries rather than project names. ATAM focuses on quality-attribute tradeoffs such as performance, availability, security, and modifiability, while Rozanski and Woods organize architecture descriptions into viewpoints and perspectives ATAM: Method for Architecture Evaluation [70], Software Systems Architecture [6] -> define K as a constraint and objective profile, not as a domain label.

- **Seven Seed Labels Are Valid, But Need Shared Mechanisms**: The seven Neural seeds naturally map to seven K classes: outbound-pipeline, content-pipeline, product-marketing, product-saas, research-memory, audit-pipeline, and intel-pipeline. Data, CMS, MLOps, and agent sources all converge on freshness, provenance, replayability, validation, and human oversight as recurring architectural drivers MLOps: Continuous delivery and automation pipelines in machine learning [63], AI Agent Systems: Architectures, Applications, and Evaluation [33] -> keep seven top-level classes for v0, then allow later merges if verification shows confusion.

- **Hard Constraints Must Be Unioned Before Soft Objectives Are Blended**: DDD shows that bounded contexts protect local model consistency, while context relationships need explicit integration patterns Use Domain Analysis to Model Microservices [79], Bounded Context [86] -> for hybrids such as LSD, decompose into sub-project contexts, union hard constraints, and blend only soft weights.

- **Knowledge Systems Explain c_find And c_derive Better Than Software Taxonomies**: Information architecture classifies organization schemes by retrieval mode, PARA classifies by actionability, Zettelkasten classifies note maturity, and Diataxis classifies documentation by user need Organization Systems in Information Architectures [1], The PARA Method [2], From Fleeting Notes to Project Notes [52], Diataxis [4] -> use these to parameterize c_find, c_loss, and c_derive in research-memory and content-pipeline classes.

- **Pipeline Classes Are Dominated By Freshness, Replay, And Drift**: Lambda separates batch, speed, and serving layers; Kappa argues for one stream-processing path to reduce dual-codebase complexity; Medallion uses Bronze, Silver, and Gold refinement stages Lambda Architecture using Azure Cosmos DB [91], Questioning the Lambda Architecture [58], Medallion Architecture [81] -> outbound, content, audit, and intel pipelines should make freshness, source state, and reprocessing explicit Z3 constraints.

- **Product Classes Are Boundary And Permission Problems First**: DDD subdomains and bounded contexts classify by business value and language/model boundaries, while SaaS architecture inherits role, data, and workflow boundaries from product use Use Domain Analysis to Model Microservices [79], Bounded Context [86] -> product-saas should rank c_modify and c_loss above c_derive once real users and RBAC exist.

- **Agentic Classes Require Trace Completeness And Budgeted Autonomy**: The AI agent survey describes agent systems around policy, memory, tools, verifiers or critics, and environment, and highlights latency versus accuracy, autonomy versus controllability, and trace completeness AI Agent Systems: Architectures, Applications, and Evaluation [33] -> high T_agent_internal classes must include tool-call logs, evaluator traces, and escalation rules as hard constraints.

- **Repo Taxonomies Are Implementation Variables, Not Primary K Classes**: Nx distinguishes standalone, package-based, and integrated repos; Bazel organizes repositories, workspaces, packages, and targets; Google describes a monolithic repository as a shared source of truth Integrated Repos vs. Package-Based Repos vs. Standalone Apps [18], Bazel: Repositories, workspaces, packages, and targets [38], Why Google Stores Billions of Lines of Code in a Single Repository [36] -> choose repo style inside A* after K determines constraints.

- **Lifecycle Should Modulate K Rather Than Constantly Replace It**: Google Cloud MLOps classifies maturity into manual, ML pipeline automation, and CI/CD pipeline automation; content lifecycle management tracks content from planning through archiving or removal MLOps: Continuous delivery and automation pipelines in machine learning [63], Content Lifecycle Management [23] -> keep K stable unless a new hard constraint dominates for two planning cycles or consumes more than roughly one-third of architecture work.

## What Published Taxonomies Actually Classify

The surveyed literatures are useful, but none directly gives the K taxonomy you need. They mostly classify one architectural lens: quality attributes, model boundaries, information retrieval, documentation intent, repository structure, content lifecycle, data refinement, automation maturity, or agent orchestration. That is good news for A*: K should be a synthesis layer that turns these lenses into a COP profile.

| Literature and source | What it classifies by | Number of classes or categories | What it explains well | Where it fails for the seven Neural seeds |
|---|---:|---:|---|---|
| Bass, Clements, Kazman lineage via SEI ATAM | Quality attributes, scenarios, risks, sensitivity points, tradeoff points | SEI summary names performance, availability, security, and modifiability as quality-attribute examples; ATAM also uses scenario and risk categories | Why architecture is a tradeoff problem, and why decisions must be evaluated against stakeholder scenarios ATAM [70] | It does not tell you whether Buuuk is an outbound pipeline or whether Personal Twin is research-memory; it gives evaluation axes, not project classes |
| Rozanski and Woods | Viewpoints and cross-cutting perspectives | Two top-level families: viewpoints and perspectives; the method enumerates multiple viewpoints/perspectives | How to separate stakeholder concerns across architecture descriptions Software Systems Architecture [6] | It helps document TUHH or SI Global Engine but does not derive a constraint profile for daily-fire agent pipelines |
| DDD subdomains and bounded contexts | Strategic business value and language/model boundaries | 3 subdomain types: core, supporting, generic; Microsoft also lists context relationship patterns including Customer-Supplier, Open Host Service/Published Language, Anti-Corruption Layer, and Separate Ways | How to split a system into cohesive bounded contexts and avoid one overloaded model Use Domain Analysis to Model Microservices [79], Bounded Context [86] | DDD handles product boundaries better than agentic pipelines, model drift, or document provenance |
| Rosenfeld and Morville information architecture | Retrieval and user mental models | 2 families: exact and ambiguous organization schemes; the cited summary includes exact schemes such as alphabetical, chronological, geographical, and ambiguous schemes such as topical, task, audience, metaphor, and hybrid | c_find: how people browse, search, and recover information Organization Systems in Information Architectures [1] | It classifies information structures, not runtime workflows, external APIs, or agent traces |
| PARA | Actionability and time horizon | 4 classes: Projects, Areas, Resources, Archives | Lightweight organization of working knowledge by actionability The PARA Method [2] | It under-specifies provenance, semantic derivation, memory retrieval, and software constraints |
| Zettelkasten | Thought maturity and note function | Ahrens-style summaries discuss fleeting notes, permanent notes, project notes, literature notes, and zettels | Long-term idea derivation and associative retrieval From Fleeting Notes to Project Notes [52] | It does not specify deployment, freshness, authorization, or audit constraints |
| Diataxis | User need in documentation | 4 forms: tutorials, how-to guides, reference, explanation | Content shape by reader intent Diataxis [4] | It classifies docs, not publishing pipelines, agent review loops, or product surfaces |
| Nx monorepo taxonomy | Repository and dependency structure | 3 workspace styles: standalone application, package-based repo, integrated repo | When integrated tooling and dependency enforcement matter Integrated Repos vs. Package-Based Repos vs. Standalone Apps [18] | Repo layout is downstream of K; it does not say whether the dominant risk is c_drift, c_loss, or c_money |
| Google monorepo and Bazel | Shared source of truth and build graph hierarchy | Google describes a monolithic repository; Bazel defines repositories, workspaces, packages, and targets | Rebuildability, dependency visibility, and package boundaries Why Google Stores Billions of Lines of Code in a Single Repository [36], Bazel build reference [38] | It is code-centric; most Neural seeds also include data, documents, emails, ads, and agent traces |
| CMS/content lifecycle | Content model, workflow, lifecycle, distribution | Strapi names lifecycle stages from planning and creation through archiving/removal; Contentful defines content models and content types | Structured content, reusable content types, review/publish flows, API-first delivery Content Lifecycle Management [23], Contentful content models [46] | It handles LSD's publishing surface but not SI Global Engine audit panels or Personal Twin memory semantics |
| Lambda and Kappa architectures | Batch versus stream processing and reprocessing path | Lambda: batch, speed, serving layers. Kappa: one stream-processing framework for both real-time and reprocessing | Freshness, replay, dual-path complexity, and serving latency Lambda Architecture using Azure Cosmos DB [91], Questioning the Lambda Architecture [58] | It explains data flow but not humans, editorial judgment, RBAC, or business conversion |
| Medallion architecture | Data quality and refinement | 3 layers: Bronze, Silver, Gold | Progressive refinement from raw source data to business-ready data Medallion Architecture [81] | It does not classify project intent or agent responsibilities |
| MLOps maturity | Process automation level | 3 levels: Level 0 manual, Level 1 ML pipeline automation, Level 2 CI/CD pipeline automation | Validation, automation, monitoring, pipeline repeatability MLOps: Continuous delivery and automation pipelines in machine learning [63] | It assumes ML lifecycle structure; several seeds are knowledge and workflow systems rather than model-training systems |
| AI agent architectures | Agent components, interaction locus, reasoning substrate, orchestration | Survey describes agent components such as policy, memory, tools, verifiers/critics, environment, and six broad agent-system categories | Planning, memory, tool use, critics, trace completeness, autonomy versus controllability AI Agent Systems [33] | It explains agent substrate but not content lifecycle, SaaS RBAC, or commercial attribution by itself |

Decision-ready insight: Use these sources as feature extractors for K. ATAM supplies quality-attribute tradeoff discipline, DDD supplies decomposition, IA/KM supplies retrieval and derivation objectives, data/MLOps supplies freshness and replay constraints, and agent literature supplies T composition and traceability. None should be copied as K directly.

## Design Principles For K In A*

For A*(I, L, K, T), K should be represented as a profile rather than a label:

```text
K_profile = {
  H_K: hard constraints,
  W_K: ranked soft-objective weights over C,
  T_K: expected human/internal-agent/external-agent composition,
  F_K: failure-mode priors,
  E_K: recommended evidence and observability artifacts
}
```

This follows the architecture literature. ATAM treats architecture as a set of tradeoffs against quality attributes and stakeholder scenarios, so K should expose the tradeoffs that matter for a project class ATAM [70]. Rozanski and Woods separate architecture views from cross-cutting perspectives, so K should not collapse all concerns into one hierarchy Software Systems Architecture [6]. DDD's bounded-context principle implies that K assignment should happen at the sub-project or bounded-context level when a project has multiple local models Bounded Context [86].

The seven C axes should be treated as soft objectives unless the project class turns one into an invariant:

| C axis | Meaning in A* | Typical classes where it dominates |
|---|---|---|
| c_find | Cost of discovering, retrieving, searching, and navigating artifacts | content-pipeline, research-memory, audit-pipeline, intel-pipeline |
| c_modify | Cost of changing code, schemas, workflows, prompts, and user-facing behavior | product-saas, product-marketing, content-pipeline |
| c_storage | Cost and complexity of storing structured, unstructured, vector, graph, and historical artifacts | research-memory, audit-pipeline, intel-pipeline |
| c_money | Direct budget, revenue, ROAS, external API cost, or spend efficiency | outbound-pipeline, product-marketing, intel-pipeline |
| c_drift | Cost of stale data, schema drift, model/prompt drift, source drift, and market drift | outbound-pipeline, content-pipeline, product-marketing, intel-pipeline |
| c_loss | Expected loss from wrong, missing, leaked, or unverifiable outputs | product-saas, audit-pipeline, research-memory |
| c_derive | Cost and value of generating new outputs from existing inputs | content-pipeline, research-memory, audit-pipeline, intel-pipeline |

The constraint hierarchy for Z3 Optimize should be:

1. Class hard constraints: non-negotiable invariants such as RBAC isolation, append-only audit log, publish cutoff, or campaign spend cap.
2. Cross-class global constraints: privacy, security, source provenance, budget ceiling, external API terms, and human escalation.
3. Ranked soft objectives: lexicographic or weighted Optimize objectives over the C axes.
4. Implementation choices: repo style, database layout, orchestration framework, queueing style, and UI structure.

Decision-ready insight: K should be the point where human architectural judgment becomes solver-readable. The class says what must never break, what may trade off, and what kind of team or agent composition will probably break first.

## The Seven-Class K Taxonomy

The table below is the recommended v0. It intentionally keeps seven classes because each Neural seed has a distinct dominant hard constraint and failure mode. Later verification may merge product-marketing with product-saas, or audit-pipeline with intel-pipeline, but doing that now would hide important cost-profile differences.

| K class | Short definition | Hard constraints that bind hardest | Ranked C profile | Characteristic T composition | Seed mapping | Most likely failure modes |
|---|---|---|---|---|---|---|
| outbound-pipeline | Daily or periodic outbound system that turns lead sources into filtered prospects, sequences, deployment, and performance analytics | 1. fresh-leads-by-cutoff. 2. deliverability-safe-send-policy. 3. idempotent contact and sequence state | c_money > c_drift > c_modify | Low T_human, high T_agent_internal, high T_agent_external through email, enrichment, CRM, Smartlead-style deploy tools | Buuuk waterfall | Deliverability decay; stale ICP filters; duplicate or non-compliant outreach |
| content-pipeline | Research-to-publication system that mines sources, drafts, audits, and publishes structured content | 1. source-provenance-required. 2. human-or-agent-audit-before-publish. 3. publishable-artifact-by-cutoff | c_derive > c_find > c_drift | Medium T_human, high T_agent_internal, medium T_agent_external for search, citation, CMS, site deploy | LSD primary class | Hallucinated citations; editorial bottleneck; content taxonomy sprawl |
| product-marketing | Product catalog plus acquisition, creative, campaign metrics, and conversion economics | 1. catalog-truth-is-source-of-record. 2. campaign-spend-and-ROAS-guardrails. 3. attribution-window-preservation | c_money > c_drift > c_modify | Medium T_human for strategy, high T_agent_internal for creative/analysis, high T_agent_external for Meta, commerce, analytics APIs | MAIKAI primary class | Attribution blindness; feed or creative drift; overspend from weak guardrails |
| product-saas | Multi-user product surface with auth, permissions, workflows, data persistence, and user-facing outputs | 1. RBAC-and-PII-isolation. 2. schema-migration-safety. 3. user-visible-output-correctness | c_modify > c_loss > c_find | High T_human engineering/product, medium T_agent_internal, medium T_agent_external for Supabase, auth, PDF/export services | TUHH dashboard; LSD secondary if publishing product is significant | Permission leaks; feature entanglement; export/report mismatch |
| research-memory | Knowledge and memory system that preserves, links, retrieves, and derives from long-lived personal or organizational memory | 1. provenance-and-link-integrity. 2. memory-isolation-and-consent. 3. reversible-or-append-only-memory-updates | c_find > c_storage > c_derive | High T_human sensemaking, high T_agent_internal for retrieval/synthesis, medium T_agent_external for embeddings/search/tools | Personal Twin | Retrieval collapse; graph/vector inconsistency; privacy leakage; semantic drift |
| audit-pipeline | Document-heavy review system that ingests evidence, preserves traceability, supports panels, and produces defensible briefings | 1. immutable-source-document-retention. 2. append-only-audit-log. 3. reviewer-signoff-for-claims | c_loss > c_find > c_derive | High T_human for accountability, high T_agent_internal for extraction/comparison, medium T_agent_external for OCR, storage, search | SI Global Engine primary class | Untraceable claims; over-summarization; reviewer disagreement hidden by automation |
| intel-pipeline | Daily or scheduled intelligence system that fans out over sources, classifies events, generates briefs, and distributes alerts | 1. fresh-data-by-cutoff. 2. source-timestamp-and-dedupe-required. 3. distribution-SLA | c_drift > c_find > c_derive | Low-to-medium T_human, high T_agent_internal, high T_agent_external for web fan-out, email, search, classification | si-global-intel; SI Global Engine secondary if it includes live market monitoring | Stale or duplicate alerts; source noise; false positive classifications |

Decision-ready insight: The classes differ less by domain noun and more by which failure is unacceptable. Outbound and product-marketing fail economically; product-saas and audit-pipeline fail by trust or loss; content and research-memory fail by provenance and retrieval; intel fails by freshness and signal quality.

## Case Studies Across The Seven Seeds

Buuuk waterfall is not just a marketing project. It is an outbound-pipeline because the system's architecture is dominated by daily write cadence, external deliverability constraints, lead freshness, deduplication, and measurable reply economics. The prior Smartlead case is a useful analog: AI bees reportedly ran B2B cold email outreach for 1,000+ companies on Smartlead and built an outbound engine with a 30% reply rate Smartlead AI bees case study. The mechanism is clear: once outbound is automated, the binding risks are not UI polish or deep knowledge retrieval; they are list quality, sequence state, deliverability, and feedback loops. A* should therefore choose architectures with immutable lead-import history, dedupe keys, send-state tracking, and analytics before it optimizes general content flexibility.

Longevity Science Daily is a content-pipeline first and product-saas second. It needs research mining, draft generation, auditor review, and publishing to a Next.js site. Contentful's content-model idea is relevant because a content model is the set of content types in a space, and content types can reference one another Contentful content models [46]. Strapi's content lifecycle model is also relevant because it frames content from planning through publishing, measurement, optimization, and archiving/removal Content Lifecycle Management [23]. The mechanism is that each article is a derived artifact that must stay connected to sources, editorial state, and publish state. A* should avoid a flat folder or pure blog architecture; LSD needs source tables, claim provenance, draft status, reviewer state, and content schema versioning.

MAIKAI is product-marketing because its hard problem is not merely selling products online. It joins catalog truth, ad creative, campaign metrics, and ROAS tracking. That means the architecture must keep product identity stable across catalog, creative, campaign, and analytics surfaces. This looks like DDD: catalog, campaign, creative, order, and analytics are separate bounded contexts with potentially different meanings of terms such as product, conversion, and audience Use Domain Analysis to Model Microservices [79]. A* should prioritize attribution integrity, spend caps, and changeable creative pipelines over a generic SaaS component hierarchy.

TUHH dashboard is product-saas because 16 real users and 4 active roles make role boundaries binding. In a research prototype, the main cost might be c_derive or c_find; with real roles, Supabase auth, RBAC, and PDF export, the dominant risks become permission leakage, incorrect user-visible outputs, and painful schema changes. ATAM's quality-attribute framing is useful here because the architecture must trade modifiability against security and correctness ATAM [70]. A* should select a boring, typed, migration-safe, RBAC-first architecture even if a more agentic architecture would move faster.

Personal Twin is research-memory because the durable asset is not content, leads, campaigns, or dashboards. It is the user's memory substrate: graph links, vector retrieval, provenance, consent, and derived synthesis. Zettelkasten explains why raw capture is not enough; knowledge systems need note maturation, linking, and durable retrieval From Fleeting Notes to Project Notes [52]. PARA adds an actionability layer with Projects, Areas, Resources, and Archives The PARA Method [2]. The mechanism is that memory value increases only if future retrieval and derivation remain trustworthy. A* should therefore prefer append-only memory events, typed memory scopes, explicit provenance, retrieval evaluation, and deletion/isolation paths.

SI Global Engine and si-global-intel share a document/intelligence substrate but differ in what failure costs most. SI Global Engine is audit-pipeline because M&A documents, audit panels, and briefings create accountability constraints. The cost of a wrong or untraceable claim is high, so c_loss dominates. si-global-intel is intel-pipeline because the daily M&A fan-out, classification, brief generation, and email distribution make freshness and dedupe binding. Data architecture sources clarify the split: Lambda and Kappa focus on timely processing and reprocessing, while Medallion emphasizes raw-to-refined lineage Lambda Architecture using Azure Cosmos DB [91], Questioning the Lambda Architecture [58], Medallion Architecture [81]. A* should give SI Global Engine append-only audit trails and signoff workflows, while si-global-intel gets daily cutoff scheduling, source freshness scoring, dedupe, and distribution-state tracking.

Decision-ready insight: The seven seeds validate K because each one changes the architecture that A* should choose. If the class label does not change the selected hard constraints, soft weights, and T composition, it is not a useful K class.

## Hybrid-Class Handling In A*

Hybrids should not be handled by simply averaging two class labels at the top level. Averages can hide contradictions. A content-pipeline wants fast publishing and flexible schemas; a product-saas wants stable permissions, migrations, and user-visible correctness. If LSD is averaged too early, the solver may underweight both editorial provenance and RBAC.

The recommended rule is sub-project decomposition first, weighted blending second:

```text
1. Decompose project P into bounded subgraphs B_i.
2. Assign each B_i a primary K_i and optional secondary K_i2.
3. Compute hard constraints: H_P = union(H_Ki) + interface_constraints.
4. If hard constraints conflict, split bounded contexts or add an anti-corruption adapter.
5. Compute soft weights only after hard constraints are satisfiable:
   W_P[j] = normalize(sum_i alpha_i * exposure_i * lifecycle_i * W_Ki[j])
6. Compose T as a vector sum over human, internal-agent, and external-agent responsibilities.
```

This aligns with DDD. Microsoft's domain-analysis guidance distinguishes strategic DDD, tactical DDD, bounded contexts, subdomains, and relationship patterns such as Anti-Corruption Layer and Separate Ways Use Domain Analysis to Model Microservices [79]. Fowler's bounded-context framing explains why one global model becomes brittle when terms mean different things in different contexts Bounded Context [86].

Recommended hybrid weights for the seeds:

| Project | Hybrid decomposition | Hard-constraint rule | Soft-weight blend |
|---|---|---|---|
| LSD | 0.65 content-pipeline, 0.35 product-saas if site/product surface matters | Union provenance, audit-before-publish, publish cutoff, and any auth/publishing-role constraints | c_derive and c_find stay high; c_modify rises if readers, admins, or editors become real users |
| MAIKAI | 0.70 product-marketing, 0.30 product-saas/catalog | Campaign guardrails and catalog truth are non-negotiable; user/product UI constraints are secondary unless checkout/account features grow | c_money dominates; c_modify rises as catalog workflows and user-facing product surfaces grow |
| SI Global Engine | 0.75 audit-pipeline, 0.25 intel-pipeline | Audit log, source retention, and signoff dominate even if live intel feed exists | c_loss dominates; c_drift is secondary unless daily monitoring becomes the main value |
| si-global-intel | 0.80 intel-pipeline, 0.20 audit-pipeline | Freshness, dedupe, and distribution SLA dominate; source traceability remains required | c_drift dominates; c_loss rises for high-stakes deal alerts |

Decision-ready insight: Hybrids should be represented as a graph of classed sub-problems, not as one fuzzy label. A* should never blend away a hard constraint.

## Lifecycle Interaction: Should K Vary Across L?

K should be stable by default, while L modulates weights and activates constraints. The reason is practical: if K changes every time priorities shift, the taxonomy stops being predictive. But lifecycle stage clearly changes architecture pressure. Google Cloud's MLOps taxonomy shows this through maturity levels: Level 0 is manual, Level 1 automates the ML pipeline, and Level 2 adds CI/CD automation MLOps: Continuous delivery and automation pipelines in machine learning [63]. Content lifecycle management shows a similar progression from planning and creation to publishing, optimization, and archiving/removal Content Lifecycle Management [23].

Recommended rule:

```text
Primary K is determined by durable artifact type and binding hard constraints.
Lifecycle L changes soft weights and constraint activation.
Change primary K only if a new hard constraint remains binding for two review cycles
or consumes more than roughly one-third of architecture change effort.
Otherwise, keep K and attach a lifecycle modifier.
```

Example: an early product-saas may temporarily look like research-memory before product-market fit because it is mostly discovery, notes, prototypes, and derivation. But once it has real users, roles, authentication, and recurring workflows, product-saas hard constraints activate. TUHH is therefore product-saas even if development began with exploratory research-memory behavior.

Lifecycle modifiers for A*:

| L stage | Modifier | Typical effect on C weights |
|---|---|---|
| explore | evidence-building, cheap reversibility | raises c_derive and c_find; lowers c_modify unless real users exist |
| bootstrap | first operational workflow | raises c_modify, c_drift, and c_money depending on class |
| production | recurring users or recurring schedule | raises c_loss, c_drift, observability, and test requirements |
| scale | more users, sources, campaigns, or agents | raises c_storage, c_money, c_modify, and coordination cost |
| audit/archive | accountability and retention | raises c_loss, c_find, provenance, and immutability |

Decision-ready insight: Let K answer "what kind of system is this under pressure?" Let L answer "which part of that pressure is active now?"

## Verification Protocol

The taxonomy is useful only if it makes predictions. The verification protocol should test whether K labels are stable, discriminative, and predictive of architecture cost.

| Test | Procedure | Passing signal | What failure means |
|---|---|---|---|
| Constraint extraction test | Give raters only a project description. Ask them to list hard constraints before assigning K | Raters converge on the same 1-3 binding constraints | Class names are too semantic and not constraint-grounded |
| Blind K assignment test | Ask 3 raters to assign primary and secondary K using a one-page rubric | High agreement on primary K; disagreements explain real hybrids | Merge confusing classes or sharpen class definitions |
| COP prediction test | Run A* with K-specific hard constraints and soft weights | Solver selects different architecture templates for different K values | K is not affecting architecture and should be revised |
| Scenario stress test | Use ATAM-style scenarios: freshness spike, API failure, RBAC bug, source contradiction, campaign overspend, memory deletion request | Predicted failure modes match class priors ATAM [70] | Failure priors are wrong or too generic |
| Lifecycle stability test | Re-label the same project at explore, bootstrap, production, and archive stages | K mostly stays stable while L changes weights | Lifecycle and class are being mixed together |
| Hybrid decomposition test | Ask raters to draw bounded contexts before choosing hybrid weights | Hybrids decompose into understandable subgraphs | Weighted blend is hiding model contradictions |
| Observed cost test | Track actual time/cost over 2-4 implementation cycles by C axis | Top predicted C axes account for most observed architecture effort | Weight vector W_K needs calibration |

Predictions the taxonomy should make for new projects:

1. If a project has daily external source fan-out, dedupe, classification, and email distribution, it should be labeled intel-pipeline, and observed costs should cluster around c_drift, c_find, external API fragility, source ranking, and distribution state.
2. If a project has real users, roles, auth, persistent objects, and exports, it should be labeled product-saas, and observed costs should cluster around c_modify, c_loss, RBAC, schema migration, and user-visible correctness.
3. If a project has high-stakes document review and briefings, it should be labeled audit-pipeline, and A* should choose append-only logs, source retention, claim provenance, and reviewer signoff even when faster summary-only designs are cheaper.
4. If a project preserves personal or organizational memory across graph and vector stores, it should be labeled research-memory, and observed costs should cluster around c_find, c_storage, c_derive, provenance, and privacy.
5. If a project connects catalog, ads, creative, spend, and conversion, it should be labeled product-marketing, and A* should prioritize attribution integrity and spend guardrails before generic product extensibility.

Decision-ready insight: Verification should not ask "does the label sound right?" It should ask "did the label predict the constraints, costs, implementation choices, and failure modes that actually appeared?"

## Synthesis

The literatures differ along mechanism, scope, tradeoff, and time horizon. ATAM and Rozanski/Woods are evaluation and description frameworks: they are broad, quality-focused, and useful when architecture decisions need stakeholder justification. DDD is a boundary framework: it is narrower but more operational for splitting models, teams, and languages. IA, PARA, Zettelkasten, and Diataxis are knowledge-organization frameworks: they explain retrieval, actionability, derivation, and user intent better than they explain runtime constraints. Repo and build taxonomies are implementation frameworks: they determine rebuildability and dependency control after the project class is known. Data, MLOps, and agent frameworks are operational frameworks: they explain freshness, replay, validation, automation, memory, tools, critics, and traceability.

The proposed K taxonomy integrates these rather than choosing one. Outbound-pipeline and intel-pipeline inherit from data freshness and agent orchestration. Content-pipeline inherits from CMS lifecycle, Diataxis, and source provenance. Product-marketing inherits from DDD boundaries plus money-weighted optimization. Product-saas inherits from quality attributes, RBAC, and modifiability. Research-memory inherits from PARA, Zettelkasten, information architecture, vector/graph retrieval, and agent memory. Audit-pipeline inherits from ATAM-style risk discipline, document provenance, and append-only evidence trails.

The non-obvious tension is that the most elegant implementation taxonomy is rarely the right K taxonomy. A monorepo, Bazel package graph, or integrated Nx workspace may be excellent, but it does not tell A* whether to protect deliverability, RBAC, memory provenance, audit traceability, or daily freshness. Conversely, a project class tells A* what must be true, but not automatically whether to use monorepo, Postgres, queues, GraphQL, or agents.

Recommended implementation path:

1. Encode the seven K profiles as static dictionaries: H_K, W_K, T_K, F_K.
2. Add a bounded-context decomposition step before every A* run.
3. Use union-of-hard-constraints for hybrids.
4. Use lifecycle modifiers to tune soft weights.
5. Run verification on the seven seeds plus 5-10 unseen projects.
6. Merge classes only if verification shows they produce indistinguishable constraints and cost predictions.

Final recommendation: ship v0 with seven K classes. Treat them as constraint profiles, not project names. The taxonomy is well-defined if a new project's K label predicts which constraints become hard, which C axes dominate, what T composition is required, and which failure modes appear first.

## References

1. *Organization Systems in Information Architectures*. https://jcsites.juniata.edu/faculty/rhodes/ida/orgSys.html
2. *The PARA Method: The Simple System for Organizing Your ...*. https://fortelabs.com/blog/para/
3. *PARA Method Template for Notion (Building a Second Brain)*. http://thomasjfrank.com/templates/para-method-template-for-notion
4. *diataxis.fr - Diátaxis*. https://diataxis.fr/
5. *The Morville/Rosenfield Approach (How To) | Information ...*. https://teamtreehouse.com/library/information-architecture/the-morvillerosenfield-approach
6. *viewpoints and perspectives - Software Systems Architecture*. https://www.viewpoints-and-perspectives.info/
7. *Software Architecture in Practice - Len Bass, Paul Clements ...*. https://books.google.com/books/about/Software_Architecture_in_Practice.html?id=qNnPEAAAQBAJ
8. *ATAM: Method for Architecture Evaluation*. http://sei.cmu.edu/documents/629/2000_005_001_13706.pdf
9. *SEI ATAM Example | PDF | Software Architecture | Scenario ...*. http://scribd.com/document/596357149/SEI-ATAM-Example
10. *Software Systems Architecture: Working with Stakeholders ...*. https://books.google.com/books/about/Software_Systems_Architecture.html?id=ka4QO9kXQFUC
11. *Domain Driven Design — The Bounded Context - Medium*. http://medium.com/%40johnboldt_53034/domain-driven-design-the-bounded-context-1a5ea7bcb4a4
12. *Software Architecture | Domain Driven Design | Understanding ...*. https://www.filipkrawiec.com/posts/software-architecture/domain-driven-design/understanding-ddd/domains-subdomains-and-bounded-context
13. *Confused About Bounded Contexts and SubDomains? Demystifying ...*. https://www.tutorialpedia.org/blog/confused-about-bounded-contexts-and-subdomains/
14. *Implementing Domain-Driven Design - Archive.org*. https://archive.org/download/ebooks_202003/Vaughn%20Vernon/Implementing%20Domain-Driven%20Design%20%281504%29/Implementing%20Domain-Driven%20Design.pdf
15. *Martin Fowler - Ubiquitous Language (bliki)*. http://martinfowler.com/bliki/UbiquitousLanguage.html
16. *Command-Line Reference - Bazel*. http://bazel-docs-staging.netlify.app/versions/master/command-line-reference.html
17. *Blazing Fast Distributed CI with Nx | by Victor Savkin - Nx Devtools*. http://blog.nrwl.io/blazing-fast-distributed-ci-with-nx-a1f5974f7393
18. *Integrated Repos vs. Package-Based Repos vs. Standalone Apps | Nx*. https://19.nx.dev/concepts/integrated-vs-package-based
19. *Solving Monorepo Hell with Bazel: A Deep Dive into Modern ...*. https://medium.com/@erfan.mohebi/solving-monorepo-hell-with-bazel-a-deep-dive-into-modern-build-systems-f70c831bb227
20. *Monorepos and Trunk-Based Development - a Perfect Match?*. https://www.linkedin.com/pulse/monorepos-trunk-based-development-perfect-match-gregory-entin
21. *Services - Everteam Software*. http://everteam.com/en/services-2
22. *Why You Need a GEO Content Strategy for the AI Search Era*. http://strapi.io/blog/geo-content-strategy
23. *What Is Content Lifecycle Management and Why Does It Matter*. https://strapi.io/blog/content-lifecycle-management
24. *Content Management Systems (CMS)*. http://3plains.com/web-services/content-management
25. *Headless Content Modeling Services for Scalable Headless CMS ...*. https://www.pathtoproject.com/services/headless-content-modeling
26. *Lambda Architecture 101: Unpacking batch, speed and serving ...*. https://www.flexera.com/blog/finops/lambda-architecture/
27. *Kappa Architecture - System Design - GeeksforGeeks*. https://www.geeksforgeeks.org/system-design/kappa-architecture-system-design/
28. *What is Medallion Architecture?*. http://databricks.com/blog/what-is-medallion-architecture
29. *Lambda architecture - Wikipedia*. https://en.wikipedia.org/wiki/Lambda_architecture
30. *Kappa Architecture 101: Deep dive into stream-first design (2026)*. https://www.flexera.com/blog/finops/kappa-architecture/
31. *Vice President, Platform Engineering - Myworkdayjobs.com*. http://vibrant.wd5.myworkdayjobs.com/veh_external_career_site/job/remote-usa/vice-president--unified-platforms_jr100156
32. *Understanding MLOps Lifecycle: From Data to Delivery and ...*. https://www.ideas2it.com/blogs/understanding-mlops-phases-data-delivery
33. *AI Agent Systems: Architectures, Applications, and Evaluation*. https://arxiv.org/html/2601.01743v1
34. *Cesar Duran*. http://linkedin.com/in/cesar-m-duran
35. *Unlock Enterprise-Ready Agentic Workflows to Power ...*. http://orkes.io/use-cases/agentic-workflows
36. *Why Google Stores Billions of Lines of Code in a Single ...*. https://research.google/pubs/why-google-stores-billions-of-lines-of-code-in-a-single-repository/
37. *nrwl/nx: The Monorepo Platform that amplifies both ...*. http://github.com/nrwl/nx
38. *Repositories, workspaces, packages, and targets | Bazel*. https://bazel.build/concepts/build-ref
39. *Why Google Stores Billions of Lines of Code in a Single ...*. https://cacm.acm.org/research/why-google-stores-billions-of-lines-of-code-in-a-single-repository/
40. *Fetched web page*. http://linkedin.com/company/nxdevtools
41. *Lisa Maria Marquis*. http://linkedin.com/in/redsesame
42. *Information Architecture - intertwingled.org*. https://intertwingled.org/information-architecture/
43. *Website Organizational Architecture (Schemes, Structures)*. https://www.seotrance.com/website-design/module6/organizational-architecture.php
44. *Dara Rosenfeld Design: Home*. http://dararosenfelddesign.com/
45. *Quark Software, Inc. | Modern Content Lifecycle Management*. http://quark.com/
46. *Content models | Contentful Help Center*. https://www.contentful.com/help/content-models/
47. *Linked entries and assets in Contentful*. http://contentful.com/blog/exploring-linked-entries-assets-contentful
48. *CMS Governance Workflows: How to Eliminate Content ...*. https://www.dotcms.com/blog/cms-governance-workflows-how-to-eliminate-content-bottlenecks-without-sacrificing-security
49. *dddcommunity.org | Domain Driven Design Community*. https://www.dddcommunity.org/
50. *GitHub - VaughnVernon/IDDD_Samples: These are the sample ...*. https://github.com/VaughnVernon/IDDD_Samples
51. *Microsoft Docs - Domain Analysis (Azure Architecture Center)*. http://learn.microsoft.com/en-us/azure/architecture/microservices/model/domain-analysis
52. *From Fleeting Notes to Project Notes – Concepts of*. https://zettelkasten.de/posts/concepts-sohnke-ahrens-explained/
53. *Zettelkasten Method: Complete Setup Guide with Templates*. https://www.atlasworkspace.ai/blog/zettelkasten-method-guide
54. *Learning The Zettelkasten Method is Easy, Actually*. https://noahvnct.substack.com/p/learning-the-zettelkasten-method
55. *Niklas Luhmann's Original Zettelkasten: Two Slip Boxes, Fixed ...*. https://www.ernestchiang.com/en/posts/2025/niklas-luhmann-original-zettelkasten-method/
56. *Types of Notes - PKM Zettelkasten*. https://zk.zettel.page/types-of-notes
57. *About Confluent*. http://confluent.io/about
58. *Questioning the Lambda Architecture – O’Reilly*. https://www.oreilly.com/radar/questioning-the-lambda-architecture/
59. *Databricks – AI Adoption*. http://dufrain.co.uk/partnerships/our-databricks-business/databricks-ai-adoption
60. *Senior Software Engineer, AI Agents (Autonomous Systems) — Gaia*. http://indeed.com/viewjob?jk=d09cbbfa93e054df
61. *How to Build AI Agents with Agentic Design Patterns Webinar*. http://tungstenautomation.com/learn/webinars/how-to-build-ai-agents-with-agentic-design-patterns
62. *Lead DevOps Engineer - Eightfold AI*. http://app.eightfold.ai/careers/job/68759038119
63. *MLOps: Continuous delivery and automation pipelines in ...*. https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning
64. [[2601.01743] AI Agent Systems: Architectures, Applications ...](https://arxiv.org/abs/2601.01743)
65. *APIs with bounded contexts - by Jose Haro Peralta - microapis.io*. http://microapis.substack.com/p/apis-with-bounded-contexts
66. *APIs using Domain Driven Design - by Shalin Garg - Medium*. http://medium.com/%40shalin.garg/apis-using-domain-driven-design-a7ecf7bb11fb
67. *Domain-­-Driven Design Reference Definitions and Pattern...*. https://www.academia.edu/41658106/Domain_Driven_Design_Reference_Definitions_and_Pattern_Summaries
68. *Bounded Contexts and Ubiquitous Language: Deciphering DDD’s ...*. https://www.paulserban.eu/blog/post/bounded-contexts-and-ubiquitous-language-deciphering-ddds-core-concepts/
69. *Software Engineering Institute | CMU Software Engineering Institute*. http://sei.cmu.edu/
70. *ATAM: Method for Architecture Evaluation*. http://sei.cmu.edu/library/atam-method-for-architecture-evaluation
71. *QA and Tactics - RIT*. https://www.se.rit.edu/~swen-440/slides/instructor-specific/Kuehl/Lecture%2017%20Quality%20Attributes%20and%20Tactics%20LV.pdf
72. *News Index | CMU Software Engineering Institute*. http://sei.cmu.edu/news
73. [Software Architecture in Practice, 4th Edition [Book]](https://www.oreilly.com/library/view/software-architecture-in/9780136885979/)
74. *  Top 7 AI Agent Orchestration Frameworks - KDnuggets*. http://kdnuggets.com/top-7-ai-agent-orchestration-frameworks
75. *Senior Full Stack Software & AI Developer - Cenovus Energy*. http://builtin.com/job/senior-full-stack-software-ai-developer/6500177
76. *Build a multiple-agent workflow automation solution by using ...*. https://learn.microsoft.com/en-us/azure/architecture/ai-ml/idea/multiple-agent-workflow-automation
77. *Actions and tool use patterns - Microsoft Copilot Studio*. http://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/architecture/action-tool-use
78. *7 best LangChain alternatives in 2026 | Zapier*. http://zapier.com/blog/langchain-alternatives
79. *Use Domain Analysis to Model Microservices - Azure Architecture Center | Microsoft Learn*. https://learn.microsoft.com/en-us/azure/architecture/microservices/model/domain-analysis
80. *Bounded Context*. https://martinfowler.com/bliki/BoundedContext.html
81. *What is Medallion Architecture? | Databricks*. https://www.databricks.com/glossary/medallion-architecture
82. *Getting Started with Contentful and .NET*. http://contentful.com/developers/docs/net/tutorials/using-net-cda-sdk
83. *Content Models | contentful/contentful.net | DeepWiki*. https://deepwiki.com/contentful/contentful.net/4-content-models
84. *http://contentful.com/developers/docs/references*. http://contentful.com/developers/docs/references
85. *The Ultimate Guide to Content Modeling in Contentful - Nansen*. https://www.nansen.com/insights/content-modeling-in-contentful
86. *Bounded Context*. http://martinfowler.com/bliki/BoundedContext.html
87. *Domain Driven Design re-distilled | by Yoan Thirion - Medium*. http://yoan-thirion.medium.com/domain-driven-design-re-distilled-685e75595a60
88. *architecture-center/docs/microservices/model/domain-analysis ...*. https://github.com/microsoftdocs/architecture-center/blob/main/docs/microservices/model/domain-analysis.md
89. *GitHub - ddd-crew/bounded-context-canvas: A structured ...*. https://github.com/ddd-crew/bounded-context-canvas
90. *Compare AWS and Azure compute services*. http://learn.microsoft.com/en-us/azure/architecture/aws-professional/compute
91. *Lambda Architecture using Azure #CosmosDB: Faster performance ...*. https://azure.microsoft.com/en-us/blog/lambda-architecture-using-azure-cosmosdb-faster-performance-low-tco-low-devops/
92. *Lambda Architecture: Bridging Batch and Real-Time*. https://blog.amsayed.dev/blog/lambda-architecture
93. *Implementing Lambda Architecture on Azure for Big Data*. https://developex.com/blog/applying-lambda-architecture-on-azure/
