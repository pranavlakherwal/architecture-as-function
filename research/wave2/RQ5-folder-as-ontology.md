# Weaken Folder Ontology Into Layered Scope Governance

## Executive Summary

- **Verdict**: The literature supports folders as meaningful navigation and context structures, but not the literal claim that every folder is an ontology in the formal RDF/OWL sense -> restructure the thesis as a layered scheme: scoped folders plus facets, tags, graphs, search, and machine-readable manifests where needed W3C OWL [102], W3C RDF [113].
- **Human Folder Advantage**: PIM studies repeatedly find that people prefer location-based folder navigation; Bergman et al. report strong folder preference over tags, with folders used for roughly **90%** of files and tags for roughly **1%** in the studied file environment -> keep hierarchy as the primary human navigation layer, but do not make it the only semantic layer Folder versus tag preference in personal information management [26].
- **Search Counterexample**: In email, Whittaker et al. instrumented **345** users and more than **85,000** refinding actions and found that complex folder preparation did not improve retrieval success relative to opportunistic methods such as search and threading -> avoid mandatory deep folder ontologies for high-volume, stream-like corpora Am I wasting my time organizing email? [33].
- **Facet Superiority In Multi-Dimensional Collections**: The Flamenco/UC Berkeley work evaluated faceted metadata on collections up to **40,000** images with **9** facets and found users understood and preferred dynamically organized faceted metadata, with final ratings at least about **6/7** for ease and usefulness -> use facets when items legitimately belong to multiple simultaneous dimensions Hierarchical Faceted Metadata in Site Search Interfaces [75].
- **Tags Are Not Enough, But Hybrids Matter**: Bergman et al. show weak tag adoption in ordinary PIM, while Voit et al. found tag-based refinding reduced interaction cost from **19.0** clicks to **13.9** clicks and **78%** of participants preferred Tagstore in one experiment -> reject pure tag-as-primary for most teams, but adopt controlled tags for cross-cutting retrieval Tagging Might Not Be Slower Than Filing in Folders [65].
- **Agent-Heavy Systems Need Explicit Semantics**: Schema.org reports structured data use across more than **45M** domains and more than **450B** marked-up objects, while a May **2026** OpenAPI-agent case study found **2,450** documentation and REST smells across **16** production APIs and **600** endpoints; original documentation failed **70%** of planning tasks, while enriched documentation achieved **90%** planning success -> for T_agent_internal high, scope declarations should be machine-readable and CI-validated Schema.org [21], Making OpenAPI Documentation Agent-Ready [24].
- **No Universal Decay Rate**: The PIM literature reviewed documents failure mechanisms such as fragmentation, out-of-sight files, misfiling, excessive depth, stale branches, and cross-tool inconsistency, but it does not establish a general decay constant like "X% of folders decay per year" -> measure local decay with repository audits rather than quoting a universal rate Too Many Hierarchies? [42], Personal information organization and re-access in computer folders [46].
- **Best Formulation**: Replace the thesis with: "Every stable folder used as a navigation, ownership, or lifecycle boundary must declare and enforce scope; the repository ontology is layered across folders, facets, tags, links, schemas, and indexes" -> this preserves the useful discipline without overstating the empirical case.

## Bottom-Line Verdict: Restructure, Do Not Keep Literal Ontology Language

The strong version, "every folder is a small ontology with declared scope," should be weakened and restructured. The evidence supports three weaker claims: folders help humans refind information through location, recognition, and contextual memory; hierarchy can encode a meaningful semantic relation when the folder has a stable decision rule; and explicit scope declarations are likely to reduce ambiguity for both humans and agents. The evidence does not support the universal claim that every folder already is, or must be treated as, an ontology.

The reason is conceptual and empirical. In formal knowledge-organization and Semantic Web usage, an ontology represents classes, relations, constraints, and sometimes inferable knowledge. OWL is described by W3C as a language for representing "rich and complex knowledge about things, groups of things, and relations between things," enabling programs to exploit expressed knowledge, verify consistency, and make implicit knowledge explicit W3C OWL [102]. A filesystem folder normally supplies one explicit structural relation: containment. Its actual semantic relation might be topic, owner, lifecycle stage, audience, task, release, source system, or simply convenience. Without a README, manifest, schema, naming convention, or validator, the semantics are often tacit.

The empirical literature therefore supports this refined claim: every stable folder should declare its scope when the folder is used as a semantic boundary. It does not support the stronger claim that folder hierarchy is a sufficient substitute for facets, tags, graph relations, or search. In fact, the best evidence points toward a multi-layered organization system.

**Decision insight:** Keep the discipline of declared folder scope, but retire the phrase "every folder is a small ontology" as the governing thesis. Use it only as a metaphor in training materials, not as the normative claim.

## What The Evidence Can And Cannot Prove

| Evidence family | What it supports | What it does not support | Decision implication |
|---|---|---|---|
| PIM and CHI/CSCW folder studies | Humans often prefer browsing, location, and folder navigation for personal refinding Finding and Reminding [60], Navigating through digital folders uses the same brain structures as real world navigation [15] | That every folder has a precise ontology, or that deep hierarchy always improves findability | Use hierarchy for primary navigation where users know the domain and refind known items |
| Email refinding studies | Search, threading, and opportunistic access can outperform elaborate folder filing in email Am I wasting my time organizing email? [33] | That folders are obsolete everywhere | Avoid mandatory folder ontologies in high-volume streams and message archives |
| Faceted classification and IA | Multiple independent dimensions improve exploration in public, multi-dimensional collections Hierarchical Faceted Metadata in Site Search Interfaces [75], Information Architecture for the World Wide Web, ch. 9 [87] | That facets eliminate the need for local containment, lifecycle ownership, or repository structure | Use facets for audience, status, product, geography, version, compliance, and other cross-cutting concerns |
| Tagging and folksonomy | Tags can support associative retrieval, but uncontrolled tags create synonym, ambiguity, and vocabulary drift problems Usage Patterns of Collaborative Tagging Systems [80], Tagging Might Not Be Slower Than Filing in Folders [65] | That tags alone reliably replace folders for ordinary PIM | Use controlled tags as a secondary layer, not as the only organization primitive unless the team accepts vocabulary governance |
| Graphs and ontologies | RDF/OWL and knowledge graphs represent relations that folder trees cannot express W3C RDF [113], W3C OWL [102] | That every project needs OWL-level formalization | Use graphs when relation density, reasoning, provenance, dependencies, or agent planning matter |
| Documentation frameworks | Diataxis supports organizing documentation around user needs: tutorials, how-to guides, reference, and explanation Diataxis [1] | That Diataxis empirically proves folder ontology | Use Diataxis as a documentation scope model, not as proof of filesystem ontology |

The central pattern is that each scheme wins under different cognitive and operational conditions. The folder tree is valuable, but it is not a universal ontology.

## Scheme-By-Scheme Survey: Findability, Maintenance, Dominance, Failure

| Scheme | Empirical evidence on user findability | Evidence on long-term maintenance | Where it dominates | Where it loses |
|---|---|---|---|---|
| Hierarchy / tree / folders | Barreau and Nardi observed **22** users across two studies and found that users relied on browsing and location more than text search for file refinding Finding and Reminding [60]. Benn et al. used fMRI with **17** participants and found digital folder navigation activates brain structures associated with real-world navigation Navigating through digital folders uses the same brain structures as real world navigation [15]. Bergman et al. found strong folder preference over tags Folder versus tag preference in personal information management [26]. | Boardman, Spence, and Sasse show that users maintain separate hierarchies across documents, email, and bookmarks, creating fragmentation Too Many Hierarchies? [42]. Folder re-access studies report limits of hierarchical folders and persistent re-finding difficulty Personal information organization and re-access in computer folders [46]. | Stable projects, known-item retrieval, ownership boundaries, lifecycle boundaries, code repositories, documentation sections, local context. | Multi-dimensional classification, highly relational domains, email, chat, logs, artifacts that belong naturally in many places. |
| Faceted classification | English et al. studied hierarchical faceted metadata with collections up to **40,000** architecture images, **9** facets, and **12** participants; users understood and preferred dynamically organized faceted metadata, with final ratings around **6/7** for ease and usefulness Hierarchical Faceted Metadata in Site Search Interfaces [75]. Rosenfeld and Morville describe facets as shifting the question from "Where do I put this?" to "How can I describe this?" Information Architecture for the World Wide Web, ch. 9 [87]. | Facets require controlled vocabularies, metadata quality, and governance. Rosenfeld and Morville treat controlled vocabularies as the glue connecting organization, labeling, navigation, and search systems Information Architecture for the World Wide Web, ch. 9 [87]. ISKO's facet-analysis entry cautions that facet analysis has been criticized for lacking empirical and pragmatic basis in some formulations Facet analysis [91]. | E-commerce, library discovery, design systems, documentation by audience/task/product/version, large public collections, analytics portals. | Small local workspaces where users need one obvious place to put or find a thing; systems without metadata discipline. |
| Tags / folksonomy | Golder and Huberman analyze collaborative tagging as an emergent classification system and show that tag use can stabilize socially over time Usage Patterns of Collaborative Tagging Systems [80]. Voit et al. found tagging was not necessarily slower than filing; in one task it reduced refinding clicks from **19.0** to **13.9** Tagging Might Not Be Slower Than Filing in Folders [65]. | Tags require vocabulary control. Without it, synonymy, homonymy, granularity variation, spelling variation, and personal idioms reduce maintenance quality Usage Patterns of Collaborative Tagging Systems [80]. Voit's TagTrees work uses generated navigational structures and restrictions to make tags usable in local file systems TagTrees [117]. | Cross-cutting concerns, lightweight associative retrieval, personal knowledge bases, status labels, topics that cut across folders. | High-compliance repositories, teams with no tag governance, artifacts needing one canonical owner/lifecycle path. |
| Graph / ontology | RDF represents data as directed labeled graphs for data interchange and merging across schemas W3C RDF [113]. OWL supports explicit classes, relations, consistency checking, and inference W3C OWL [102]. A 2025 ontology/KG RAG preprint reports **90%** accuracy for graph/ontology approaches with chunks versus **60%** for a vector baseline on **20** domain questions, but this is early and narrow evidence Ontology Learning and Knowledge Graph Construction [84]. | Graphs need schema governance, relationship typing, identifiers, tooling, and migration practices. The maintenance burden shifts from folder placement to model curation. | Dependency networks, provenance, APIs, regulated data, enterprise knowledge graphs, agent planning, relation-heavy code and docs. | Simple repositories, small teams, low relation density, teams without graph tooling or schema ownership. |
| Flat plus search | Whittaker et al. show that in email, preparatory folder filing can be inefficient; search and threading can support effective refinding without complex folder structures Am I wasting my time organizing email? [33]. | Maintenance burden is low because users file less, but long-term quality depends on naming, content text, indexing, deduplication, retention, and search quality. | Email, chat, logs, temporary corpora, high-volume append-only archives, full-text-rich artifacts. | Ambiguous artifact names, weak metadata, regulated retention, agent workflows requiring explicit constraints, tasks requiring browsing or lifecycle governance. |

**Decision insight:** The best-supported design is not hierarchy-only. It is hierarchy for primary navigation and accountability, facets/tags for cross-cutting classification, graph relations for dependencies and reasoning, and search for high-volume retrieval.

## Case Study 1: Folders Work Because Humans Remember Places

Barreau and Nardi's classic desktop study synthesized two empirical studies of **22** users across Macintosh, DOS, Windows, and OS/2 settings. Users generally preferred browsing visible locations and file lists over text search, and they used files and desktop locations not only for storage but also for reminding themselves what needed attention Finding and Reminding [60]. This is the strongest human-centered evidence for keeping folders as first-class structures.

Benn et al. add a cognitive mechanism. Their fMRI study with **17** participants found that navigating digital folders activated posterior limbic and parahippocampal regions associated with real-world navigation, while search engaged more language/executive resources Navigating through digital folders uses the same brain structures as real world navigation [15]. That does not prove a folder is an ontology, but it does show that folder paths can become embodied, spatial retrieval cues.

Bergman et al. provide the strongest direct folder-vs-tag PIM evidence. Their study of environments where users had both folders and tags found a strong preference for folders for both storage and retrieval; extracted figures from the source showed folders used for roughly **90%** of files and tags for roughly **1%** Folder versus tag preference in personal information management [26]. The implication is that, for human-heavy teams and known-item refinding, hierarchy is not merely cosmetic. It is part of the user's memory system.

But these studies still support a weaker conclusion than "folder equals ontology." They show that folders are useful location and context cues. They do not show that the parent-child relation has one stable semantic meaning, or that every folder has declared classes, constraints, and relations.

**Decision insight:** Treat folders as scoped cognitive landmarks. Require scope declarations for stable folders, but do not infer formal ontology from containment alone.

## Case Study 2: Email Shows When Folder Ontology Fails

Whittaker et al.'s CHI 2011 study is the most important counterexample to a universal folder thesis. The researchers instrumented a modern email client and analyzed behavior from **345** long-term users and more than **85,000** refinding actions Am I wasting my time organizing email? [33]. They specifically studied users who invested preparatory effort in folder organization.

The finding cuts against the strong folder claim: complex folder structures did not reliably improve retrieval success, and opportunistic methods such as search and threading often supported more effective refinding. In this domain, information is stream-like, duplicated across conversations, and rich in searchable text. The cost of maintaining a strict folder ontology can exceed its retrieval benefit.

The mechanism is important. Email messages often have many plausible categories: sender, project, task, time, urgency, thread, attachment, customer, or status. A single folder path forces one placement decision at save time, while later retrieval may use a different cue. This is exactly the condition under which facets, tags, search, or conversation graphs dominate.

**Decision insight:** Do not impose folder-as-ontology on stream corpora such as email, chat, ticket comments, logs, or notification archives. Use search, threading, retention rules, and lightweight tags instead.

## Case Study 3: Facets Beat Trees When Items Need Multiple Paths

Ranganathan's Colon Classification, first published in **1933**, is the classic knowledge-organization argument against a single enumerated hierarchy. ISKO's entry explains that Colon Classification uses analytico-synthetic classification and the PMEST facets: Personality, Matter, Energy, Space, and Time Colon Classification [88]. Ranganathan's Five Laws, including the principle commonly summarized as "save the time of the reader," provide a normative service orientation for organization, but they are not direct empirical proof that folder trees are sufficient.

Rosenfeld and Morville make the same point for web information architecture. Their controlled-vocabulary chapter defines hierarchical relations, associative relations, synonym rings, thesauri, taxonomies, and facets as different tools in the IA system. They report a Bellcore study in which synonym rings increased recall from **20%** to **80%**, but with possible precision trade-offs Information Architecture for the World Wide Web, ch. 9 [87]. Their framing is especially relevant: faceted classification changes the question from "Where do I put this?" to "How can I describe this?"

The Flamenco/UC Berkeley work gives empirical support. English, Hearst, Sinha, Swearingen, and Yee evaluated hierarchical faceted metadata in site search. In an architecture slide collection of more than **40,000** images, using **9** facets and roughly **10** metadata items per slide, **12** participants gave the refined interface high ratings, with ease and usefulness at least about **6/7** Hierarchical Faceted Metadata in Site Search Interfaces [75]. Hearst's later design recommendations emphasize facet hierarchy navigation, label layout, facet exposure, breadcrumbs, and keyword search as design elements Design Recommendations for Hierarchical Faceted Search Interfaces [95].

**Decision insight:** If an artifact naturally belongs to multiple dimensions, the primary ontology should not be a folder tree. Use folders for custody and locality, and facets for classification.

## Case Study 4: Tags Are Weak Alone, Strong As Controlled Cross-Cuts

The evidence on tags is mixed. Bergman et al. found that ordinary PIM users strongly preferred folders over tags when both were available Folder versus tag preference in personal information management [26]. Golder and Huberman's collaborative tagging work shows why: tags can form useful emergent structures, but they also introduce synonymy, ambiguity, spelling variation, and level-of-specificity problems Usage Patterns of Collaborative Tagging Systems [80].

Voit's TagTrees work is the strongest counterweight. In "Tagging Might Not Be Slower Than Filing in Folders," Voit, Andrews, and Slany used a repeated-measures design with **18** participants and **30** items. Across all participants, folder filing was faster than tagging, but tagging reduced refinding interaction cost from **19.0** clicks to **13.9** clicks, and **78%** of participants preferred the Tagstore system Tagging Might Not Be Slower Than Filing in Folders [65]. Voit's dissertation expanded this into TagTrees, a hybrid approach that generates navigational folder-like structures from assigned tags, with a second formal experiment involving **27** participants and **60** files with a two-week gap between filing and refinding TagTrees [117].

The lesson is not "tags replace folders." It is that tags can generate alternate navigation paths when governed and tool-supported. That directly contradicts the strong sub-thesis implication that tags or facets are not sufficient substitutes in all cases. They are insufficient as unmanaged folksonomy, but powerful as controlled secondary layers.

**Decision insight:** Use controlled tags for cross-cutting concerns and generated views. Do not make free tags the only source of truth unless the repository has tag governance, disambiguation, and cleanup protocols.

## Case Study 5: Agents Need Schemas More Than They Need Folders

The agent-team angle strengthens the case for explicit semantics, but not necessarily for folder-first ontology. RDF is a W3C model for data interchange that represents data as directed labeled graphs and supports merging across schemas W3C RDF [113]. OWL builds on Semantic Web foundations to represent complex knowledge, relations, and consistency constraints W3C OWL [102]. Schema.org provides shared structured-data vocabularies used by search engines and applications; the site reports more than **45M** domains and more than **450B** marked-up objects Schema.org [21].

API and schema standards point in the same direction. JSON Schema is a declarative language for describing and validating JSON data JSON Schema [115]. OpenAPI provides a machine-readable description format for HTTP APIs, allowing humans and computers to discover and understand service capabilities without source-code access or extra documentation OpenAPI Specification [114]. These standards are closer to formal scope contracts than ordinary folder names are.

The emerging agent evidence is directly relevant but should be treated cautiously because some sources are recent preprints. A May **2026** OpenAPI-agent case study evaluated **16** production APIs and **600** endpoints, found **2,450** documentation and REST smells, and reported that agents using original documentation failed **70%** of planning tasks while enriched documentation produced **90%** planning success Making OpenAPI Documentation Agent-Ready [24]. A 2025 ontology/KG RAG preprint reported **90%** accuracy for graph/ontology retrieval with chunks versus **60%** for vector RAG on **20** domain questions Ontology Learning and Knowledge Graph Construction [84]. These are not broad settled laws, but they support the mechanism: agents benefit from explicit, machine-readable constraints because they cannot rely on tacit team context.

**Decision insight:** For T_agent_internal high, the right primitive is not just "folder." It is a folder plus manifest plus schema plus graph links plus validation. Agents need explicit declarations, not merely human-readable placement.

## What Fails As Folder Hierarchies Age

The literature supports failure modes more strongly than it supports a precise decay rate. I did not find an established, generalizable rate such as "folder hierarchies decay by X% per year." The studies are heterogeneous: they involve personal files, email, bookmarks, lab tasks, desktop observations, and prototypes. They document mechanisms and interventions, not a universal decay constant.

| Aging failure mode | What the literature shows | Decay rate status | Intervention |
|---|---|---|---|
| Dead branches and stale folders | Folder trees can preserve old project structures after work has moved on; users then stop browsing those branches. PIM studies describe re-access difficulty and the limits of hierarchical folders Personal information organization and re-access in computer folders [46]. | No universal rate found. | Report folders with no recent writes, no reads, no owner, or no valid README. Archive rather than delete by default. |
| Orphan files | Files lose their retrieval context when placed outside the intended structure or when a project spans tools. Boardman et al. describe project fragmentation across documents, email, and bookmarks Too Many Hierarchies? [42]. | No universal rate found. | Require owner, project, lifecycle, and source metadata for stable artifacts. Generate orphan reports. |
| Mis-categorization | Single-location placement fails when an item has multiple plausible meanings. Rosenfeld and Morville's IA treatment of facets directly addresses this problem Information Architecture for the World Wide Web, ch. 9 [87]. | No universal rate found. | Use facets/tags for cross-cutting dimensions. Allow aliases or graph links rather than duplicate files. |
| Scope creep inside folders | A folder starts with a coherent rule, then accumulates exceptions. This is implied by PIM findings on filing difficulty and reorganization Finding and Reminding [60]. | No universal rate found. | Require a folder manifest with in-scope, out-of-scope, allowed artifact types, and examples. Review exceptions. |
| Excessive depth or breadth | Folder navigation depends on remembering paths and recognizing locations; structure affects navigation performance The effect of folder structure on personal file navigation [53]. | No universal rate found. | Keep folder depth and fan-out within locally tested limits. Use tree testing for IA. |
| Out-of-sight, out-of-mind | Barreau and Nardi show files and locations serve reminding functions; hidden files are easier to forget Finding and Reminding [60]. | No universal rate found. | Use dashboards, recent/stale views, task lists, and generated indexes. |
| Cleanup overcorrection | Recent PIM work on deletion suggests deletion may be under-adopted but can also harm retrieval success and satisfaction in some conditions Deletion Considered Harmful [119]. | Emerging evidence, not settled. | Prefer quarantine, retention classes, and reversible archival to aggressive deletion. |

**Decision insight:** Do not claim a decay rate unless your own repository measures one. Add local metrics: no-scope folder ratio, orphan file ratio, stale branch ratio, cross-scope violation rate, duplicate artifact count, invalid tag count, and manifest coverage.

## Agent-Team Angle: How T_agent_internal Changes The Recommendation

For human-heavy systems, implicit semantics can work for a while. People use memory, team norms, conversation, and visual location to infer why a file is in a folder. That is why PIM studies find strong navigation preference and why folder trees remain useful Navigating through digital folders uses the same brain structures as real world navigation [15], Folder versus tag preference in personal information management [26].

For agent-heavy systems, tacit semantics are a liability. Agents need explicit affordances: what this folder contains, what it excludes, what schemas artifacts must satisfy, what relations point outward, what lifecycle rules apply, and what tools can operate safely. The W3C RDF/OWL stack, Schema.org, JSON Schema, and OpenAPI all encode this principle in different domains: machine consumers need stable identifiers, structured attributes, validatable shapes, and typed relations W3C RDF [113], W3C OWL [102], Schema.org [21], JSON Schema [115], OpenAPI Specification [114].

| T condition | Folder-as-ontology fit | Better primitive | Required governance |
|---|---|---|---|
| T_human_internal high, T_agent_internal low | Good as a metaphor if folder names and READMEs are clear | Folder tree plus README | Naming conventions, owner, examples, tree testing |
| T_human_internal high, T_agent_internal high | Incomplete | Folder tree plus machine-readable manifest | JSON/YAML manifest, JSON Schema validation, generated index, CI checks |
| T_agent_internal high, cross-folder reasoning high | Weak | Graph or ontology overlay | RDF/OWL or typed graph, stable IDs, relation vocabulary, reasoner or graph queries |
| T_external_users high | Weak alone | IA system: hierarchy plus facets plus search | Controlled vocabulary, faceted metadata, search analytics, tree tests |
| T_distributed_team high | Risky if implicit | Scoped folders plus governance | Code owners, review workflows, manifest coverage, exception register |

**Decision insight:** The higher T_agent_internal is, the more the system should shift from "folder semantics are understood" to "folder semantics are declared, machine-readable, and enforceable."

## Conditions By Project Class K And Team Vector T

Because the prompt does not define K formally, I use K here as the project knowledge-organization class: the dominant structure of the work and its artifacts. T is the team vector, especially human-heavy versus agent-heavy operation.

| Project class K | Typical artifacts | Best primary primitive | Why | Folder-as-ontology verdict |
|---|---|---|---|---|
| K1 - Modular build or codebase | Source files, tests, docs, configs | Scoped folders | Locality, build boundaries, ownership, imports, and lifecycle often align | Strong fit if each stable directory has README/manifest and CI rules |
| K2 - Documentation site | Tutorials, how-to guides, reference, explanations | Diataxis-like hierarchy plus facets | Diataxis organizes docs around user needs and forms Diataxis [1] | Good as primary navigation, but facets for product, version, audience, and task |
| K3 - Research/data project | Raw data, derived data, notebooks, protocols, outputs | Scoped folders plus metadata manifests | Lifecycle and provenance matter; artifacts need validation | Good if manifests declare provenance, schema, owner, and retention |
| K4 - Multi-audience content library | Articles, assets, media, components | Faceted classification | Items belong to multiple dimensions at once | Folder-only loses; facets dominate |
| K5 - High-volume communication stream | Email, chat, logs, tickets | Flat plus search, thread graph, retention rules | Preparatory filing is often costly; search and threading work well | Folder ontology usually loses |
| K6 - Dependency or provenance network | APIs, services, entities, data lineage, knowledge base | Typed graph or ontology | Relations matter more than containment | Folder tree is only a storage layer; graph dominates |
| K7 - Personal or small-team knowledge base | Notes, references, snippets | Hybrid folders plus controlled tags | Users benefit from location and associative retrieval | Folder plus tags dominates; pure ontology likely overkill |
| K8 - Agent-operated repository | Tools, schemas, prompts, APIs, generated artifacts | Machine-readable manifests plus schemas and graph links | Agents require explicit constraints for planning and safe action | Folder-as-ontology must become folder-as-contract |

**Decision insight:** Folder-as-ontology is the right primitive only when the dominant relation is containment, ownership, lifecycle, or local module scope. It loses when the dominant relation is multi-membership, sequence/threading, dependency, provenance, or inference.

## Recommended Refined Formulation

Use option (c), with option (b) embedded as an enforcement rule.

> **Refined Sub-thesis 2:** A repository should expose a layered, enforceable knowledge-organization scheme. Each stable folder that functions as a navigation, ownership, lifecycle, or execution boundary must declare its scope, allowed artifacts, exclusions, owner, and maintenance rules. The folder tree is the primary locality and human-navigation layer, not the whole ontology. Cross-cutting meanings must be represented as controlled facets or tags; relation-dense meanings must be represented as typed links, schemas, or graphs. For agent-heavy systems, scope declarations must be machine-readable and validated.

This formulation preserves the empirical strengths of folders while removing the unsupported universal claim. It also aligns with Diataxis for documentation, IA/faceted classification for multi-dimensional collections, and Semantic Web/API schema practice for machine-readable systems Diataxis [1], Information Architecture for the World Wide Web, ch. 9 [87], W3C OWL [102], OpenAPI Specification [114].

### Minimum Enforcement Protocol

For every stable semantic folder, require a README or manifest with these fields:

| Field | Purpose | Human-heavy version | Agent-heavy version |
|---|---|---|---|
| Scope | States what belongs here | README paragraph | `scope` field in YAML/JSON |
| Out of scope | Prevents scope creep | Examples and anti-examples | `exclusions` array |
| Allowed artifact types | Prevents mixed containers | List in README | JSON Schema enum or file-pattern rule |
| Owner | Assigns maintenance accountability | Team or person | CODEOWNERS plus manifest owner |
| Lifecycle | Distinguishes draft, active, deprecated, archive | Status table | Controlled lifecycle vocabulary |
| Required metadata | Supports refinding and validation | Checklist | JSON Schema or OpenAPI component schema |
| Relations | Captures cross-folder meaning | Links section | RDF/JSON-LD/typed graph edge list |
| Review cadence | Prevents silent decay | Date in README | CI stale-check rule |

CI or repository automation should then check: manifest exists, required fields are present, files match allowed patterns, links resolve, owners are valid, stale folders are reported, generated indexes are current, tags come from controlled vocabularies, and exceptions are explicitly registered.

**Decision insight:** The intervention is not "make every folder an ontology." The intervention is "make every stable folder a scoped, testable contract, and model non-containment semantics in the right layer."

## Synthesis: The Folder Is A Contract, Not The Ontology

The literature creates a clear tension. PIM research says humans like folders, remember locations, and often reject tags as primary organization. Email research says folder preparation can waste effort. IA and faceted-classification research says single hierarchies fail when users need multiple paths. Semantic Web and API-schema research says agents need explicit machine-readable semantics, but those semantics are richer than folder containment.

These findings are not contradictory once each scheme is assigned to the right job. Hierarchy handles locality, ownership, lifecycle, and known-item navigation. Facets handle multi-dimensional description. Tags handle lightweight associative cross-cuts. Graphs handle typed relationships, provenance, dependency, and inference. Search handles high-volume text and streams. Formal schemas and ontologies handle agent-safe interpretation.

The strong A* sub-thesis overclaims by collapsing all of those layers into the folder tree. A better thesis treats folders as scoped contracts in a larger knowledge-organization stack. In a human-heavy codebase, a README-declared folder may be enough. In an agent-heavy repository, the same folder needs a manifest, JSON Schema, typed relations, generated indexes, and validation. In a public documentation system, the folder tree should be supplemented by Diataxis structure, facets, and search analytics. In a graph-like domain, the folder path should not pretend to be the ontology.

**Final recommendation:** restructure the claim. Do not say "every folder is a small ontology" as an empirical assertion. Say: "Every stable folder is a scoped semantic boundary that must declare and enforce its contract; the repository ontology is layered across folders, facets, tags, graphs, schemas, and search."

## References

1. *diataxis.fr - Diátaxis*. https://diataxis.fr/
2. *Information Architect Job Description | UX Staffing Agency*. http://artisantalent.com/job-descriptions/information-architect-job-description
3. *Welcome to Coginiti Documentation | Coginiti Documentation*. http://docs.coginiti.co/intro
4. *Controlled Vocabularies - Information Architecture for the ...*. https://www.oreilly.com/library/view/information-architecture-for/0596000359/ch09s02.html
5. *Interpretable Context Methodology: Folder Structure as ...*. https://arxiv.org/pdf/2603.16021
6. *Advances in Knowledge Organization*. https://iskoproceedings.org/
7. *(PDF) Folksonomies: (Un)Controlled Vocabulary? - ResearchGate*. https://www.researchgate.net/publication/28807454_Folksonomies_UnControlled_Vocabulary
8. *International Society for Knowledge Organization*. http://en.wikipedia.org/wiki/International_Society_for_Knowledge_Organization
9. *An adaptive semantic retrieval framework for digital ... - Nature*. https://www.nature.com/articles/s41598-025-24276-1
10. *ISKO: International Society for Knowledge Organization*. https://www.isko.org/
11. *Folder vs . Tag Preference in Personal Information Management*. https://www.semanticscholar.org/paper/Folder-vs-.-Tag-Preference-in-Personal-Information-Bergman/06299855330e614ed965730da9d78b5ff495d810
12. *The future of personal information management in the age of ...*. https://www.tandfonline.com/doi/pdf/10.1080/07370024.2025.2482191
13. *Fetched web page*. http://sasse.de/impressum
14. *Google Scholar*. https://scholar.google.com/
15. *Navigating through digital folders uses the same brain ...*. https://www.nature.com/articles/srep14719
16. *UDC Seminar 2017*. http://seminar.udcc.org/2017
17. *Facet analysis: The logical approach to knowledge ...*. https://www.sciencedirect.com/science/article/pii/S0306457312001203
18. *Colon classification — Grokipedia*. https://grokipedia.com/page/Colon_classification
19. *Understanding Faceted Classification in Library and ...*. https://www.lisedunetwork.com/understanding-faceted-classification-in-library-and-information-science/
20. *CoLIS: Conceptions of Library and Information Sciences*. http://wikicfp.com/cfp/program?id=534
21. *Schema.org - Schema.org*. https://schema.org/
22. *OpenAPI Specification - Version 3.1.0 - Swagger*. http://swagger.io/specification
23. *Software That Understands the Work, Not Just the Worker*. http://arraycorp.com/vertical-industry-ontologies
24. *Making OpenAPI Documentation Agent-Ready: Detecting ...*. https://arxiv.org/html/2605.14312v1
25. *From Semantic Web and MAS to Agentic AI: - arXiv.org*. https://arxiv.org/html/2507.10644
26. *Folder versus tag preference in personal information management*. https://onlinelibrary.wiley.com/doi/full/10.1002/asi.22906
27. *Folder versus tag preference in personal information management*. https://onlinelibrary.wiley.com/doi/10.1002/asi.22906
28. *New AI Enhancements Available in Cloud: January 2026 ...*. http://answers.laserfiche.com/questions/233614/New-AI-Enhancements-Available-in-Cloud-January-2026December-2025
29. *Folder vs. Tag Preference in Personal Information - BIU*. https://is.biu.ac.il/files/is/Folders%20vs%20Tags%20-%20Preprint%20version.pdf
30. *Michelle Whittaker-McCracken, CPC, SPHR*. http://linkedin.com/in/michelle-whittaker-mccracken-cpc-sphr-565125
31. *(PDF) Am I wasting my time organizing email? - ResearchGate*. https://www.researchgate.net/publication/221518713_Am_I_wasting_my_time_organizing_email
32. *Contact - The Whittaker Group LLC.*. http://whittakergroup.org/contact
33. *Am I wasting my time organizing email? | Proceedings of the ...*. https://dl.acm.org/doi/abs/10.1145/1978942.1979457
34. *90+ "Michele Whittaker" profiles - LinkedIn*. http://linkedin.com/pub/dir/Michele/Whittaker/us-0-United-States
35. *The Science of Managing Our Digital Stuff - MIT Press*. https://mitpress.mit.edu/9780262035170/the-science-of-managing-our-digital-stuff/
36. *The Science of Managing Our Digital Stuff | MIT Press ...*. https://academic.oup.com/mit-press-scholarship-online/book/22884
37. *The Science of Managing Our Digital Stuff - Ofer Bergman ...*. https://books.google.com/books/about/The_Science_of_Managing_Our_Digital_Stuf.html?id=us2MEAAAQBAJ
38. *The Science of Managing Our Digital Stuff - Ofer Bergman ...*. https://books.google.com/books/about/The_Science_of_Managing_Our_Digital_Stuf.html?id=Ds1uDQAAQBAJ
39. *The science of managing our digital stuff - Bar-Ilan University*. https://cris.biu.ac.il/en/publications/the-science-of-our-digital-stuff/
40. *Commonwealth Roofing Corp.*. http://members.agcky.org/directory/Details/commonwealth-roofing-corp-2254100
41. *Commonwealth Roofing Company Profile*. http://datanyze.com/companies/commonwealth-roofing/28429465
42. *Too Many Hierarchies?*. http://www.cs.ucl.ac.uk/fileadmin/sec/publications/Boardman_Spence_Sasse_Too_Many_Hierarchies_HCI2003.pdf
43. *"Stuff goes into the computer and doesn't come out ...*. https://dl.acm.org/doi/abs/10.1145/985692.985766?download=true
44. *Commonwealth Roofing: Employee Directory | ZoomInfo.com*. http://zoominfo.com/pic/commonwealth-roofing-corp/28429465
45. *LibGuides: Research Data Management : Managing Files*. https://guides.lib.virginia.edu/RDM/file-management
46. *Personal information organization and re-access in computer ...*. https://www.ideals.illinois.edu/items/26602
47. *Folder structure – Reproducible Research Things - GitHub Pages*. https://orchid00.github.io/ReproducibleResearchThings/03-folderstructure/index.html
48. *PERSONAL INFORMATION ORGANIZATION AND RE-ACCESS IN ... - CORE*. https://core.ac.uk/download/pdf/4834287.pdf
49. *Organizing Data Files - Data Management Toolkit @ UNH ...*. https://libraryguides.unh.edu/datamanagement/organize
50. *Understanding and Improving Personal File Retrieval*. https://www.semanticscholar.org/paper/Understanding-and-Improving-Personal-File-Retrieval-Fitchett/29c35b674cbf8924650b7951584dbc322a20f44b
51. *Navigating through digital folders uses the same brain ...*. https://ui.adsabs.harvard.edu/abs/2015NatSR...514719B/abstract
52. *Understanding and Improving Personal File Retrieval*. https://ir.canterbury.ac.nz/items/ba7b1b0d-97fa-4f70-a021-1238688d4ee2/full
53. *The effect of folder structure on personal file navigation*. https://onlinelibrary.wiley.com/doi/abs/10.1002/asi.21415
54. *The Project Fragmentation Problem in Personal Information ...*. https://dl.acm.org/doi/epdf/10.1145/1124772.1124813
55. *Keeping Found Things Found - ScienceDirect*. https://www.sciencedirect.com/book/edited-volume/9780123708663/keeping-found-things-found
56. *Finders, keepers? The present and future perfect in support ...*. https://www.researchgate.net/publication/220167363_Finders_keepers_The_present_and_future_perfect_in_support_of_personal_information_management
57. *Intentional Information Fragmentation in Email Management*. https://vtechworks.lib.vt.edu/items/5578fdef-a1ca-4b37-8785-148edd462ab6
58. *Keeping Found Things Found: The Study and Practice of ...*. https://books.google.com/books/about/Keeping_Found_Things_Found.html?id=27UoYdWnitUC
59. [Detail by Entity Name - Sunbiz.org - Division of Corporations](http://search.sunbiz.org/Inquiry/CorporationSearch/SearchResults?Detail=FL.DOS.Corporations.Shared.Contracts.FilingRecord&InquiryDirectionType=PreviousRecord&InquiryType=EntityName&ListNameOrder=SKYDIVESPACECENTER P960000953930&SearchNameOrder=SKYDIVESPACECOAST P010000159200&SearchTerm=Skydive Mia, Inc.)
60. *Finding and Reminding: File Organization from the Desktop*. https://www.ibiblio.org/msmckoy/spring2006/articles/fileOrganizationFromTheDesktop.pdf
61. *http://northamptonma.gov/Directory/Home/SingleStaff?EID=49*. http://northamptonma.gov/Directory/Home/SingleStaff?EID=49
62. *Finding and Reminding*. https://ia801504.us.archive.org/26/items/perm1_20220428_0403/Finding.pdf
63. *Finding and reminding: file organization from the desktop ...*. https://dl.acm.org/doi/10.1145/221296.221307
64. *TagTrees: Improving Personal Information Management Using ...*. https://karl-voit.at/tagstore/en/papers.shtml
65. *Tagging Might Not Be Slower Than Filing in Folders - Karl Voit*. https://karl-voit.at/tagstore/downloads/Voit2012a.pdf
66. *Property Image | LinkedIn*. http://linkedin.com/company/property-image
67. *Tag and Find Files Fast: Metadata Tags in File Explorer*. https://windowsforum.com/threads/tag-and-find-files-fast-metadata-tags-in-file-explorer.387048/
68. *TagTrees : improving personal information management using ...*. https://repository.tugraz.at/publications/5pwdt-sn341
69. *Personal information organization and re-access in computer ...*. https://dl.acm.org/doi/10.5555/2521372
70. *11 ideas for how to organize digital files - microsoft.com*. https://www.microsoft.com/en-us/microsoft-365/business-insights-ideas/resources/11-ideas-for-how-to-organize-digital-files
71. *Welcome to Laserfiche WebLink*. http://doccenter.cityofevanston.org/WebLink
72. *Supporting multiple paths to objects in information ...*. https://www.sciencedirect.com/science/article/pii/S0306457309000739
73. *Faceted search: 9 best practices to improve UX and ...*. http://fact-finder.com/blog/faceted-search
74. *Flamenco Home*. https://flamenco.berkeley.edu/
75. *Hierarchical Faceted Metadata in Site Search Interfaces*. https://bailando.berkeley.edu/papers/chi02_short_paper.pdf
76. *Modeling Reusable and Interoperable Faceted Browsing Systems ...*. https://pmc.ncbi.nlm.nih.gov/articles/PMC5392185/
77. *Controlled Vocabulary | Practical UX Method*. http://chandan.design/ux-methods/controlled-vocabulary
78. *Collaborative tagging as a knowledge organisation and ...*. https://pureportal.strath.ac.uk/en/publications/collaborative-tagging-as-a-knowledge-organisation-and-resource-di
79. *Usage patterns of collaborative tagging systems - Scott A ...*. https://journals.sagepub.com/doi/10.1177/0165551506062337
80. *http://arxiv.org/pdf/cs/0508082*. http://arxiv.org/pdf/cs/0508082
81. *OWL-S - Wikipedia*. http://en.wikipedia.org/wiki/OWL-S
82. *Accepted Main Conference Papers - EMNLP 2025*. http://2025.emnlp.org/program/main_papers
83. *OG-RAG: Ontology-grounded retrieval-augmented ...*. http://aclanthology.org/2025.emnlp-main.1674.pdf
84. *Ontology Learning and Knowledge Graph Construction: A ...*. https://arxiv.org/html/2511.05991v1
85. *Fetched web page*. http://reports.adviserinfo.sec.gov/reports/ADV/152622/PDF/152622.pdf
86. *Directory Structure | Data Management*. https://datamanagement.hms.harvard.edu/plan-design/directory-structure
87. *Information Architecture - Fucinaweb*. https://fucinaweb.com/materiale/iaftwww/ch09.pdf
88. *Colon Classification (IEKO) - International Society for ...*. https://www.isko.org/cyclo/colon_classification
89. *About | Divio Documentation*. http://docs.divio.com/documentation-system
90. *Faceted Search | Springer Nature Link*. https://link.springer.com/book/10.1007/978-3-031-02262-3
91. *Facet analysis (IEKO) - International Society for Knowledge ...*. https://www.isko.org/cyclo/facet_analysis
92. *Musings on Faceted Search, Metadata, and Library Discovery ...*. https://www.tandfonline.com/doi/full/10.1080/01639374.2023.2222120
93. *Faceted classification - Wikipedia*. https://en.wikipedia.org/wiki/Faceted_classification
94. *Review of Techniques in Faceted Search Applications*. https://ieeexplore.ieee.org/document/9297275
95. *Design Recommendations for Hierarchical Faceted Search Interfaces*. https://flamenco.berkeley.edu/papers/faceted-workshop06.pdf
96. *Searching for Titles*. http://help.bibliocommons.com/hc/en-us/articles/31765683992084-Searching-for-Titles
97. *Finding the flow in web site search | Communications of the ACM*. https://dl.acm.org/doi/10.1145/567498.567525
98. *Search Facets - The Digital Platform Documentation Site*. http://docs.gossinteractive.com/article/11060/Search-Facets
99. *Web Ontology Language: OWL2 - Stony Brook University*. http://www3.cs.stonybrook.edu/~pfodor/courses/CSE595/L05_Web_Ontology_Language_OWL2.pdf
100. *Making OpenAPI Documentation Agent-Ready: Detecting ...*. https://www.semanticscholar.org/paper/Making-OpenAPI-Documentation-Agent-Ready%3A-Detecting-Lima-Pinheiro/22c160e2eea5ffeb13677d6007b4b2e630a045dc
101. *Schema.org - Schema.org*. http://schema.org/
102. *OWL - Semantic Web Standards*. https://www.w3.org/OWL/
103. *Why API Documentation is Insu cient for Developers: an ...*. http://yuyue.github.io/res/paper/Why%20API%20Doc-SCIS%202019.pdf
104. *Diátaxis*. http://diataxis.fr/
105. *Dara Rosenfeld Design: Home*. http://dararosenfelddesign.com/
106. *Tree Testing: Fast, Iterative Evaluation of Menu Labels and ...*. http://nngroup.com/articles/tree-testing
107. *Established Frameworks and Models in Information Architecture*. https://informationarchitectureauthority.com/ia-frameworks-and-models
108. *What is Diátaxis and should you be using it with your ...*. https://idratherbewriting.com/blog/what-is-diataxis-documentation-framework
109. *9 "Nirmal Ranganathan" profiles*. http://linkedin.com/pub/dir/Nirmal/Ranganathan
110. *Five laws of library science - Wikipedia*. https://en.wikipedia.org/wiki/Five_laws_of_library_science
111. *Five Laws of Library Science by Ranganathan*. https://www.lisedunetwork.com/five-laws-of-library-science/
112. *(PDF) Colon Classification (CC) - ResearchGate*. https://www.researchgate.net/publication/321985821_Colon_Classification_CC
113. *RDF - Semantic Web Standards*. https://www.w3.org/RDF/
114. *OpenAPI Specification v3.2.0*. https://spec.openapis.org/oas/latest.html
115. *JSON Schema - What is JSON Schema?*. https://json-schema.org/overview/what-is-jsonschema
116. *GitHub - novoid/tagstore: a research software; a fun way of ...*. https://github.com/novoid/tagstore
117. *TagTrees: Improving Personal Information Management Using ...*. https://www.karl-voit.at/tagstore/downloads/Voit2012b.pdf
118. *Don't Do Complex Folder Hierarchies - They Don't Work and ...*. https://karl-voit.at/2020/01/25/avoid-complex-folder-hierarchies/
119. *Deletion Considered Harmful - arXiv.org*. https://arxiv.org/pdf/2512.23907
120. *Cleaning Up Orphaned Files and Folders in Document ...*. https://positiveresults.com/blog/technology/cleaning-up-orphaned-files-and-folders/
121. *Mastering Directory & Folder Structures: Best Practices ...*. https://systemsize.com/folder-comparison/mastering-directory-folder-structures-best-practices-explained/
122. *data-science-tutorials/useful-python-scripts-file-tasks/stale ...*. https://github.com/balapriyac/data-science-tutorials/blob/main/useful-python-scripts-file-tasks/stale_folder_purger.py
123. *$OrphanFiles May Not Be What You Think - LinkedIn*. https://www.linkedin.com/pulse/orphanfiles-may-what-you-think-jeff-hamm-cwsge
124. *Communications Department*. http://roanokecountyva.gov/84/Communications-Department
125. *Mood and personal information management: how we feel ...*. https://link.springer.com/content/pdf/10.1007/s00779-020-01412-4.pdf
