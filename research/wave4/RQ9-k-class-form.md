# RQ9 - The Form of K in A*(I, L, K, T): Fixed Taxonomy, Inheritance Lattice, or Free Constraint-Bag?

**Wave 4 research memo. Replaces a Parallel.ai ultra2x run. Claude Code native deep search (WebSearch + WebFetch).**

## Executive Summary

- **Recommendation.** Adopt the **inheritance lattice** form for K in v0.2 of A\*. The seven v0 classes stay as the **bootstrap base**; new K-profiles are derived from them via four formal operators (`lift_tenant`, `restrict_scope`, `compose`, `specialize_tenant`). This is a strict superset of v0 (every fixed class is a 0-step derivation), it cleanly classifies `/Core/Neural/neural-gtm/` as `lift_tenant(outbound-pipeline)`, and it preserves the W_K simplicity prior via inheritance along the derivation chain.
- **Why not fixed taxonomy.** Three of the eight Neural projects already fail to fit one v0 class cleanly: `neural-gtm` (engine), LSD (content + product-saas hybrid), Personal Twin (research-memory + intel-pipeline). Library science learned this lesson in the 1930s: enumerative classification (Dewey) does not scale; faceted classification (Ranganathan) does ([Faceted classification, Wikipedia](https://en.wikipedia.org/wiki/Faceted_classification); [Comparison of DDC and LCC, Wikipedia](https://en.wikipedia.org/wiki/Comparison_of_Dewey_and_Library_of_Congress_subject_classification)). Biology learned it again with cladistics replacing Linnaean ranks for new lineages ([Cladistics, New World Encyclopedia](https://www.newworldencyclopedia.org/entry/Cladistics)). Software architecture learned it a third time: the GoF 23 patterns stopped growing; pattern languages (POSA, microservices.io with 44 patterns and counting) kept growing because they admit derivation and composition ([Design Patterns, Wikipedia](https://en.wikipedia.org/wiki/Design_Patterns); [Microservices.io](https://microservices.io/patterns/)).
- **Why not free constraint-bag.** The bag form loses the prior. v0 leans hard on W_K defaults from K to get a usable scalar objective in Z3 Optimize (see `impl/a_star/solver/model.py`, lines 140-188). Without per-class defaults, every folder reinvents weights, drift across folders climbs, and the simplicity prior H_simp from RQ8 has no anchor. The DDD bounded-context literature warns explicitly that free per-context modeling **fails to tell you how to identify the boundary in practice** ([Domain-driven design, Wikipedia](https://en.wikipedia.org/wiki/Domain-driven_design)).
- **Strongest evidence for lattice.** Faceted classification (PMEST, Colon Classification) demonstrates 90 years of working derivation in a knowledge-organization system; OWL subclass hierarchies and Haskell typeclass hierarchies (Wadler/Blott 1989) demonstrate working derivation in formal systems with mechanical soundness checks ([Wadler & Blott 1989](https://dl.acm.org/doi/pdf/10.1145/75277.75283); [Type class, Wikipedia](https://en.wikipedia.org/wiki/Type_class)); Cedar's entity hierarchy with `memberOfTypes` shows that lattice-shaped membership is sufficient for industrial authorization ([Cedar Entities](https://docs.cedarpolicy.com/policies/syntax-entity.html)).
- **Strongest counter-evidence.** Lattices add specification surface. Every operator is a place where you can write a wrong derivation and produce a wrong K. Cladistics taxonomies famously fight over which clades are valid; OWL ontologies famously suffer from open-world reasoning surprises ([The Open World Assumption Considered Harmful](https://douroucouli.wordpress.com/2020/09/04/the-open-world-assumption-considered-harmful/)). v0.2 contains the risk by (a) requiring all derivations resolve to one of the seven bootstrap classes at the leaves, (b) requiring every operator declare a soundness condition that preserves H/W/T/F/E well-formedness, (c) gating any newly derived K through a one-time engineering review before it is allowed in production solver runs.

## Part A - The Question and the Trigger

A\* v0 defines `K = (H_K, W_K, T_K, F_K, E_K)` where:
- `H_K` = hard constraints (must hold for the architecture to be feasible)
- `W_K` = ranked C_core soft weights (drives the scalarized Z3 Optimize objective)
- `T_K` = required tool capabilities (e.g., SMTP for outbound, vector index for research-memory)
- `F_K` = required manifest fields
- `E_K` = excluded patterns (forbidden artifact types)

K is the constraint **profile**. v0 fixes K to a closed taxonomy of seven named classes drawn from the live Neural portfolio at freeze date 2026-05-21. The trigger for RQ9: v0.1 consolidation (2026-05-22) split the AgencyA repo into Layer A engine `/Core/Neural/neural-gtm/` plus Layer B tenant `/Core/Neural/AgencyA/`. The engine is tenant-agnostic, ships pipelines rather than being one, has no leads, no SMTP, no end-users. It does not fit any of the seven v0 classes. Forcing K=outbound-pipeline (what we did during the consolidation solver run) is a category error: the H_K rider `suppression_list scope must have a canonical assignment` is vacuous against an engine that has no leads to suppress.

Three candidate forms for K in v0.2:

1. **Fixed taxonomy** (v0 + extensions). Add an 8th class `engine-of-K`, then a 9th, 10th when the next meta-pattern shows up. Every new pattern means a new class.
2. **Inheritance lattice**. Derive new K-profiles from the seven bootstrap classes via formal operators. `engine-of(outbound-pipeline)` is produced by `lift_tenant(outbound-pipeline)`. The seven stay frozen; the lattice grows mechanically.
3. **Free constraint-bag**. K dissolves as a named entity. Every folder declares its own `(H, W, T, F, E)` in `.manifest.yaml`. Predicates compose. Maximum expressiveness, minimum prior.

The rest of the memo is a literature survey across taxonomy-form, pattern-catalog growth, and constraint-modeling; a formal lattice spec; a per-project empirical fit table; a COP encoding sketch for each form; and a recommendation with falsifiers.

## Part B - Literature Survey: Taxonomy Form (Task 1)

### B.1 Biological taxonomy: Linnaean ranks (enumerative) versus phylogenetic clades (derived)

Linnaean classification predates the theory of evolution by a century and a half. It uses a fixed set of ranks (kingdom, phylum, class, order, family, genus, species) and assigns each organism to exactly one branch at each rank. Cladistics, introduced by Willi Hennig in the mid-20th century, replaces ranks with monophyletic clades and uses **derived characters** (synapomorphies) as the inclusion criterion.

> "In contrast to the traditional Linnaean system of classification, phylogenetic classification names only clades. Traditional Linnaean taxonomy uses several fixed levels of a hierarchy, such as Kingdom, Phylum, Class, Order, and Family, whereas cladistics does not use those terms because one of its fundamental premises is that the evolutionary tree is very deep and very complex, and it is not meaningful to use a fixed number of levels."
> -- [New World Encyclopedia, Cladistics](https://www.newworldencyclopedia.org/entry/Cladistics)

The relevant lesson for A\*: **fixed-rank schemes break when the domain has no natural finite set of ranks**. The Neural portfolio is an evolving domain. New pattern classes (engine-of-X, harness-of-X, lab-of-X) keep appearing. A fixed taxonomy forces us to either pick a wrong class or grow the list every quarter. Cladistics-style derivation places a new pattern at the right point in the derivation graph without invalidating the older classes.

The counter-evidence is real: cladistic systems suffer from disputes over which features count as synapomorphies, and the same is true for the lattice in A\* (which operator do I apply?). The mitigation: keep the operator set small (four) and require explicit declaration, not inference, of the derivation expression.

References:
- [Cladistics - New World Encyclopedia](https://www.newworldencyclopedia.org/entry/Cladistics)
- [Incompatibility of Cladistic and Linnaean Systems - Palaeos](http://palaeos.com/systematics/taxonomy/incompatible.html)
- [Using trees for classification - UC Berkeley Understanding Evolution](https://evolution.berkeley.edu/phylogenetic-systematics/using-trees-for-classification/)

### B.2 Library science: Dewey (enumerative) versus LCC (semi-faceted) versus Ranganathan PMEST (fully faceted)

The Dewey Decimal Classification (DDC, 1876) is a fixed enumerative hierarchy: ten classes, each subdivided to ten, recursively. It was designed for medium-sized libraries (under 200,000 items) and **struggles structurally to add new top-level subjects** without restructuring the entire scheme.

> "DDC was designed for medium-sized libraries, while LCC allows libraries with larger collections to be more specific or precise with classifications, making DDC preferred by institutions with collections under 200,000, while LCC is recommended if the collection includes more than 500,000 items."
> -- [Comparison of Dewey and LCC, Wikipedia](https://en.wikipedia.org/wiki/Comparison_of_Dewey_and_Library_of_Congress_subject_classification)

Library of Congress Classification (LCC) is more growable because it has **no length limit on notation**. But it inherits LCSH's well-documented problem of embedded outdated language; updates are reactive, not systematic ([Library of Congress Classification, Wikipedia](https://en.wikipedia.org/wiki/Library_of_Congress_Classification); [Rethinking the Library of Congress Classification - LitHub](https://lithub.com/we-need-to-radically-rethink-the-library-of-congress-classification/)).

Ranganathan's faceted classification (Colon Classification, 1933) is the strongest precedent for a lattice-shaped knowledge organization. He proposed five fundamental categories - PMEST (Personality, Matter, Energy, Space, Time) - that combine **analytico-synthetically** to express any subject ([PMEST - LIS Education Network](https://www.lisedunetwork.com/ranganathans-pmest-the-foundation-of-faceted-classification/)).

> "An enumerative classification contains a full set of entries for all concepts. A faceted classification system uses a set of semantically cohesive categories that are combined as needed to create an expression of a concept."
> -- [Faceted classification, Wikipedia](https://en.wikipedia.org/wiki/Faceted_classification)

> "New facets may be created at any time without disruption of a single hierarchy or reorganizing other facets [...] faceted classification systems make few assumptions about the scope and organization of the domain. It is difficult to break a faceted classification schema."
> -- [Faceted classification, Wikipedia](https://en.wikipedia.org/wiki/Faceted_classification)

For A\*, PMEST is a near-perfect analogue of the K-profile tuple `(H, W, T, F, E)`. Both are small fixed sets of orthogonal axes that combine to express an instance. The relevant lesson: **a small fixed set of derivation primitives plus mechanical combination scales to a domain of arbitrary growth**, where adding a new top-level concept does not require restructuring.

References:
- [PMEST: Ranganathan's Five Fundamental Categories - LIS Education Network](https://www.lisedunetwork.com/ranganathans-pmest-the-foundation-of-faceted-classification/)
- [Faceted classification - Wikipedia](https://en.wikipedia.org/wiki/Faceted_classification)
- [Fundamental categories: facets and facet analysis - INFLIBNET](https://ebooks.inflibnet.ac.in/lisp2/chapter/fundamental-categories-facets-and-facet-analysis-principles-of-facet-sequence-or-citation-order/)
- [Comparison of Dewey and LCC - Wikipedia](https://en.wikipedia.org/wiki/Comparison_of_Dewey_and_Library_of_Congress_subject_classification)
- [We Need to Radically Rethink the Library of Congress Classification - LitHub](https://lithub.com/we-need-to-radically-rethink-the-library-of-congress-classification/)

### B.3 Ontology engineering: OWL subclass hierarchies and open-world reasoning

OWL (Web Ontology Language) is the W3C standard for derivation-based class hierarchies. Classes can be defined extensionally (enumeration of members) or **intensionally** (a class is the set of all members satisfying a logical formula). Subclass hierarchies are **derived** from these definitions by a reasoner, not declared.

The key tension is the open-world assumption (OWA). OWA says: if you have not asserted P, P is not known to be false (it might just be unknown). This is the opposite of database closed-world reasoning and is essential for ontologies that merge across organizations.

> "Ontology formalisms such as OWL are explicitly built on the Open World Assumption (OWA), whereas traditional database systems use the Closed World Assumption (CWA). In OWL, the absence of information is not a contradiction; it's simply unknown."
> -- [OWL overview, U. Washington / Bill Howe](https://homes.cs.washington.edu/~billhowe/cs410/owl_overview.pdf) (summarized in search result)

OWA scales to growth (new asserts never invalidate old ones) but creates surprising non-results ("why didn't my reasoner conclude X?"). For A\*, we want the growth property without the reasoner surprises: the lattice **derivation must be explicit, not inferred**.

References:
- [What are OWL Ontologies? - U. Washington](https://homes.cs.washington.edu/~billhowe/cs410/owl_overview.pdf)
- [The Open World Assumption Considered Harmful](https://douroucouli.wordpress.com/2020/09/04/the-open-world-assumption-considered-harmful/)
- [Disjointness, open and local closed world reasoning - Owlready2](https://owlready2.readthedocs.io/en/latest/disjoint.html)
- [The Open World Assumption: Elephant in the Room - Bergman](https://www.mkbergman.com/852/the-open-world-assumption-elephant-in-the-room/)

### B.4 Type theory: nominal vs structural typing

In nominal typing (Java, C#), a type is what you call it. Two types with identical structure are different types. In structural typing (TypeScript, OCaml's row polymorphism, Go's interfaces), a type is what it does: any value with the right shape satisfies the type. Haskell's typeclasses are a third pattern: ad-hoc polymorphism where membership in a class is **declared per instance**, separately from the data type definition ([Wadler & Blott, 1989](https://dl.acm.org/doi/pdf/10.1145/75277.75283); [Type class, Wikipedia](https://en.wikipedia.org/wiki/Type_class)).

> "Type classes [...] permit overloading of arithmetic operators such as multiplication, and generalise the 'eqtype variables' of Standard ML."
> -- Wadler & Blott, 1989, as summarized in [Type class, Wikipedia](https://en.wikipedia.org/wiki/Type_class)

Typeclasses form a **lattice with inheritance**: `Eq a => Ord a` means every `Ord` instance must first be an `Eq` instance. New types can join existing classes (or be excluded from them) without modifying the class definition.

For A\*, the typeclass model is the most attractive formal precedent. The seven v0 classes correspond to base typeclasses. A new K-profile derives from one or more of them; the inheritance is explicit; the soundness of any operation requires the derivation to be well-typed.

Related result: Liskov's Substitution Principle (LSP) formalizes when a derived class can stand in for its base ([Liskov substitution principle, Wikipedia](https://en.wikipedia.org/wiki/Liskov_substitution_principle)). For K in A\*, LSP gives us a soundness condition: a derived K must satisfy every hard constraint of its parent K. We use this in Part E.

References:
- [Wadler & Blott, How to Make Ad-Hoc Polymorphism Less Ad Hoc, POPL 1989](https://dl.acm.org/doi/pdf/10.1145/75277.75283)
- [Type class - Wikipedia](https://en.wikipedia.org/wiki/Type_class)
- [Type Systems: Structural vs. Nominal typing explained - Jamie Kyle, Medium](https://medium.com/@thejameskyle/type-systems-structural-vs-nominal-typing-explained-56511dd969f4)
- [An Overview of Nominal-Typing versus Structural-Typing in OOP - arXiv 1309.2348](https://arxiv.org/pdf/1309.2348)
- [Liskov Substitution Principle - Wikipedia](https://en.wikipedia.org/wiki/Liskov_substitution_principle)

### B.5 Constraint logic programming: constraint set vs constraint profile

In CLP and constraint modeling languages (MiniZinc, OR-Tools), a **constraint set** is the unordered collection of constraints in a single model. A **constraint profile** (sometimes called a model family or model template) is a higher-level description that can be instantiated to many constraint sets. MiniZinc's global constraint library and OR-Tools' CP-SAT model template patterns are examples ([MiniZinc Handbook](https://docs.minizinc.dev/en/stable/)).

> "MiniZinc features a large library of pre-defined constraints, making modelling complex relationships simple. MiniZinc promotes the use of global constraints to model well-known structures in problems, which improve the clarity of the model and allow solvers to use the most effective method to exploit the structure."
> -- [MiniZinc Handbook](https://docs.minizinc.dev/en/stable/), summarized

The pattern matches A\*'s K perfectly. K is the **profile** that gets instantiated into a constraint set at solve time. The fixed-taxonomy form keeps a small finite library of profiles; the lattice form lets us derive new profiles; the bag form discards the profile abstraction entirely.

References:
- [MiniZinc Handbook 2.9.5](https://docs.minizinc.dev/en/latest/)
- [MiniZinc - Wikipedia](https://en.wikipedia.org/wiki/MiniZinc)
- [Global constraints - MiniZinc Handbook 2.5.0](https://www.minizinc.org/doc-2.5.0/en/lib-globals.html)

## Part C - Literature Survey: Pattern-Catalog Growth (Task 2)

### C.1 GoF design patterns: 23 patterns, frozen, criticized

The Gamma/Helm/Johnson/Vlissides 1994 book catalogued 23 object-oriented design patterns. It became the defining reference and **stopped growing**. Critics quickly noted that many patterns are workarounds for missing language features (Norvig: 16 of 23 patterns disappear in Lisp/Dylan), and that the catalog cannot easily absorb new architectural patterns at higher levels of abstraction ([Design Patterns, Wikipedia](https://en.wikipedia.org/wiki/Design_Patterns)).

> "Peter Norvig demonstrates that 16 out of the 23 patterns in the Design Patterns book (which is primarily focused on C++) are simplified or eliminated (via direct language support) in Lisp or Dylan."
> -- [Design Patterns, Wikipedia](https://en.wikipedia.org/wiki/Design_Patterns)

The lesson: **a fixed catalog atrophies**. A K-form that requires editing the master list every time a new project shape appears is structurally fragile.

### C.2 POSA: growable but not derivable

The Pattern-Oriented Software Architecture series (Buschmann et al., 1996, 2000, 2004, 2007) grew past the GoF set to cover concurrency, distribution, and resource management. POSA showed that **a pattern catalog can keep growing** if you accept that patterns are added by editorial decision rather than derived from existing patterns.

> "Pattern-Oriented Software Architecture is a system of patterns capable of describing and documenting large-scale applications, and a pattern system provides a pool of proven solutions to recurring design problems and shows how to combine individual patterns into heterogeneous structures."
> -- [POSA series description, ResearchGate](https://www.researchgate.net/publication/228722744_Pattern-oriented_software_architecture)

POSA shows that pure growth (without derivation) works at human-curation speed. A\* runs faster than human-curation speed (every Neural project iteration changes the constraint profile). We need derivation.

### C.3 DDD: free-form bounded contexts

Eric Evans's Domain-Driven Design treats each bounded context as **its own model**, with its own vocabulary, defined per project. The literature on bounded contexts is candid about the cost.

> "Critics of domain-driven design argue that developers must typically implement a great deal of isolation and encapsulation to maintain the model as a pure and helpful construct. Additionally, DDD just fails to clearly tell how to identify bounded contexts in practice."
> -- [Domain-driven design, Wikipedia](https://en.wikipedia.org/wiki/Domain-driven_design)

> "Determining where one bounded context begins and another leaves off is more of an art than a science."
> -- [Bounded Context, Martin Fowler](https://www.martinfowler.com/bliki/BoundedContext.html)

For A\*, the free-bag form is the DDD analogue: every folder declares its own constraints. The DDD literature warns us that this is unguided and that practitioners reinvent boundaries inconsistently. A\* must avoid that failure mode.

### C.4 Microservices patterns: semi-closed and still growing

Chris Richardson's microservices.io catalog currently lists 44 patterns and is updated as new patterns mature in industry ([microservices.io patterns](https://microservices.io/patterns/); [Microservices Patterns, Manning](https://www.manning.com/books/microservices-patterns)). The catalog is **semi-closed**: it has structure (categorized by service decomposition, transaction management, etc.) but accepts new patterns by editorial review. This is closer to POSA than to GoF.

### C.5 Data Mesh: data product as architectural quantum, derived from domain

Zhamak Dehghani's data mesh defines the **data product as an architectural quantum** - the smallest independently deployable unit - and ties its identity to the **domain** it serves ([Data Mesh Principles, Martin Fowler](https://martinfowler.com/articles/data-mesh-principles.html); [Data Mesh, InfoQ](https://www.infoq.com/news/2020/12/data-mesh-architecture/)).

> "A data product is defined as an architectural quantum (an independently deployable, high-cohesive component encompassing all the structural elements required for its function)."
> -- Summarized from search results on data mesh

Data mesh is the closest contemporary precedent for **architectural-pattern as a derived entity**: the pattern is not picked from a menu; it is derived from the domain plus a few fixed structural rules (four principles: domain ownership, data as a product, self-service infrastructure, federated computational governance). This validates the lattice approach for A\*.

References for Part C:
- [Design Patterns - Wikipedia](https://en.wikipedia.org/wiki/Design_Patterns)
- [The Gang of Four Gave Us 23 Design Patterns - Are They Still Relevant?](https://medium.com/@freddy.dordoni/the-gang-of-four-gave-us-23-design-patterns-are-they-still-relevant-in-2025-f2e999c384c0)
- [Research state of the art on GoF design patterns - ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0164121213000757)
- [POSA - ResearchGate](https://www.researchgate.net/publication/228722744_Pattern-oriented_software_architecture)
- [Bounded Context - Martin Fowler](https://www.martinfowler.com/bliki/BoundedContext.html)
- [microservices.io patterns - Chris Richardson](https://microservices.io/patterns/)
- [Microservices Patterns, Manning](https://www.manning.com/books/microservices-patterns)
- [Data Mesh Principles, Martin Fowler](https://martinfowler.com/articles/data-mesh-principles.html)
- [Data Mesh Architecture - InfoQ](https://www.infoq.com/news/2020/12/data-mesh-architecture/)

## Part D - Literature Survey: Constraint-Modeling Form (Task 3)

### D.1 Constraint profiles in CP-SAT and MiniZinc

CP solvers (Z3 Optimize included) consume a flat constraint set at solve time, but model **builders** universally maintain a layered abstraction: parameter file -> model template -> instantiated model. MiniZinc separates `.mzn` (model) from `.dzn` (data) precisely so the same model template can be reused across many instances ([MiniZinc Handbook](https://docs.minizinc.dev/en/stable/)). OR-Tools' Python API encourages a similar pattern with `cp_model.CpModel()` builders.

The relevant mapping for A\*:
- v0's `KProfile` class in `impl/a_star/profiles/__init__.py` plays the role of the model template
- The folder-fact introspection plays the role of the data file
- `build_model(facts, k_class)` instantiates the constraint set

The fixed-taxonomy form treats KProfile as a closed dict. The lattice form treats it as a function `derive: (base_profile, operator_chain) -> profile`. The bag form discards KProfile and reads constraints directly from each folder's manifest.

### D.2 FODA feature modeling: a lattice of valid configurations

Kang et al.'s Feature-Oriented Domain Analysis (1990, CMU/SEI-90-TR-021) introduced feature models as the basis for software product line engineering ([FODA Feasibility Study, CMU SEI](https://www.sei.cmu.edu/library/feature-oriented-domain-analysis-foda-feasibility-study/); [Feature-oriented domain analysis, Wikipedia](https://en.wikipedia.org/wiki/Feature-oriented_domain_analysis)).

A feature model is a tree of features with mandatory/optional/alternative nodes and requires/excludes constraints. The **set of valid configurations** forms a lattice (closed under feature-subset operations consistent with the constraints). New product variants are derived from the same feature model by selecting a different valid configuration.

> "A feature model is a hierarchical diagram that represents the common and variable characteristics - known as features - of a family of related software products within a software product line, along with their dependencies and constraints to define valid product configurations."
> -- [Feature model, Wikipedia](https://en.wikipedia.org/wiki/Feature_model)

For A\*, FODA is the most precise precedent for a constraint-derivation lattice in software. The seven v0 K-classes correspond to common feature sets; new K-profiles correspond to valid configurations derived by selecting different feature subsets under the FODA constraints.

### D.3 Configuration management: role hierarchy

Puppet, Chef, and Ansible all support some form of role inheritance. Puppet's class inheritance, Chef's role inheritance via `run_list`, Ansible's role dependencies in `meta/main.yml` ([Ansible vs Puppet vs Chef, RedHat](https://www.redhat.com/en/topics/automation/understanding-ansible-vs-terraform-puppet-chef-and-salt); [Ansible vs Puppet vs Chef, IPSpecialist](https://ip-specialist.medium.com/ansible-vs-puppet-vs-chef-a5fbee6ff4a9)). In practice, inheritance in config management is criticized as fragile (too many subtle conflicts at merge time) and most modern deployments favor **composition** (apply role A, then role B, then role C) over inheritance.

Lesson for A\*: prefer composition (the `compose` operator) over deep inheritance chains. Limit depth to two or three derivation steps.

### D.4 Policy as code: OPA/Rego and Cedar

OPA/Rego provides rule composition through packages and imports; rules can call other rules; policies can be merged at decision time ([OPA Policy Language](https://www.openpolicyagent.org/docs/policy-language); [OPA introduction, CNCF](https://www.cncf.io/blog/2020/08/13/introducing-policy-as-code-the-open-policy-agent-opa/)). There is no formal inheritance, but composition through `import` is the standard pattern.

> "OPA lets multiple teams contribute independent policies that you can then combine to make an overall decision, with each team writing their policy in a separate package, then writing one more policy that imports all the teams' policies and makes a decision."
> -- [OPA documentation summary](https://www.openpolicyagent.org/docs)

Cedar (AWS authorization language) supports **entity hierarchy** with explicit `memberOfTypes` declarations and the `in` operator for hierarchy walks ([Cedar Entities](https://docs.cedarpolicy.com/policies/syntax-entity.html); [Cedar Schema](https://docs.cedarpolicy.com/schema/schema.html)). This is structurally the same as a typeclass lattice and confirms that industrial authorization systems have converged on derivation-based class hierarchies.

> "Entities can be grouped into logical hierarchies by specifying a parent attribute that points to the group of which the entity is a member. If the memberOfTypes element is empty or not defined, entities of that entity type can't have parents in the entity hierarchy."
> -- [Cedar Entities documentation](https://docs.cedarpolicy.com/policies/syntax-entity.html)

References for Part D:
- [MiniZinc Handbook 2.9.5](https://docs.minizinc.dev/en/latest/)
- [FODA Feasibility Study, CMU SEI](https://www.sei.cmu.edu/library/feature-oriented-domain-analysis-foda-feasibility-study/)
- [Feature-oriented domain analysis, Wikipedia](https://en.wikipedia.org/wiki/Feature-oriented_domain_analysis)
- [Feature model - Wikipedia](https://en.wikipedia.org/wiki/Feature_model)
- [Ansible vs. Terraform vs. Puppet vs. Chef - RedHat](https://www.redhat.com/en/topics/automation/understanding-ansible-vs-terraform-puppet-chef-and-salt)
- [OPA Policy Language docs](https://www.openpolicyagent.org/docs/policy-language)
- [Introducing Policy as Code: OPA - CNCF](https://www.cncf.io/blog/2020/08/13/introducing-policy-as-code-the-open-policy-agent-opa/)
- [Cedar Policy Language reference](https://docs.cedarpolicy.com/)
- [Cedar Entities](https://docs.cedarpolicy.com/policies/syntax-entity.html)
- [Cedar: A New Language for Expressive, Fast, Safe, and Analyzable Authorization, Amazon Science](https://assets.amazon.science/96/a8/1b427993481cbdf0ef2c8ca6db85/cedar-a-new-language-for-expressive-fast-safe-and-analyzable-authorization.pdf)

## Part E - Formal Lattice Operators (Task 4)

If K is a lattice, the seven v0 classes are the bootstrap elements; new K-profiles are produced by applying one or more of the following four operators. Each operator takes one or more K-profiles and returns a new K-profile. The output must satisfy the well-formedness condition `WF(K) = K = (H_K, W_K, T_K, F_K, E_K) where H_K is a satisfiable conjunction, W_K is a nonnegative weight vector over C_core that sums to a finite value, T_K and F_K are sets, and E_K is a pattern set disjoint from F_K`.

Recall the seven v0 base classes (from `A_STAR_v0.md` §K):

| id | example tenant |
|---|---|
| outbound-pipeline | AgencyA |
| content-pipeline | LSD (primary) |
| product-marketing | BrandB |
| product-saas | UniversityC |
| research-memory | Personal Twin |
| audit-pipeline | SI Engine |
| intel-pipeline | deskd-intel |

### E.1 `lift_tenant(K_in) -> K_out`

**Intent.** Turn a tenant-specific class into its tenant-agnostic engine class. Produces the `engine-of-K_in` family.

**Input.** A K-profile that targets one tenant.

**Output.** A K-profile that targets the engine layer.

**Transformation rules.**

```
H_out = H_in
      \ {hard constraints that reference tenant-specific entities like leads, end-users, billing}
      ∪ {hard constraints on reusability: api_stability, semver, no_tenant_secret_at_rest, no_tenant_data_at_rest}

W_out = renormalize(
          W_in
          with c_modify weight bumped (engine changes hit N tenants),
          with c_money weight reduced (engine has no direct revenue),
          with c_drift weight bumped (engine interface drift breaks all consumers)
        )

T_out = T_in
      \ {tenant-specific tools: SMTP, Stripe, Shopify, end-user-auth}
      ∪ {engine-specific tools: package registry, semver tagging, contract tests}

F_out = F_in
      \ {tenant-specific required fields: tenant_id, end_user_consent_basis}
      ∪ {engine-specific required fields: api_version, supported_tenants, deprecation_policy}

E_out = E_in
      ∪ {patterns excluded for engines: tenant_data/*, tenant_secrets/*, end_user_pii/*}
```

**Soundness condition.** `H_out` is satisfiable; W_out remains nonnegative and finite; F_out and E_out remain disjoint; the engine layer is not required to read or write any tenant-scoped artifact (consistency with v0.1 seam invariants).

**Worked example.** `lift_tenant(outbound-pipeline) = neural-gtm`. Drops `fresh-leads-by-cutoff` (no leads in the engine), keeps `deliverability-safe-send` as a **library contract** (engine ships the SMTP rate-limiter, doesn't run it), adds `engine-api-semver` as a new hard constraint, adds `tenant_secrets/*` to E_K.

### E.2 `restrict_scope(K_in, scope_pred) -> K_out`

**Intent.** Narrow an existing class to a subdomain (e.g., outbound restricted to B2B-only, content restricted to long-form-only, product-saas restricted to single-tenant).

**Input.** A K-profile and a predicate `scope_pred` that selects a strict subset of the original scope.

**Output.** A K-profile applicable only to the restricted scope.

**Transformation rules.**

```
H_out = H_in ∪ {scope_pred_holds(artifact)}
W_out = W_in        (no change in defaults; specialization preserves preferences)
T_out = T_in        (may be reduced via post-derivation prune)
F_out = F_in ∪ {required fields specific to the narrower scope}
E_out = E_in ∪ {patterns valid in K_in but invalid in the narrower scope}
```

**Soundness condition.** `scope_pred` is decidable on artifacts; `H_out` is satisfiable (the narrower scope must be nonempty); resulting profile is a strict refinement (Liskov-style: every K_out instance is a valid K_in instance).

**Worked example.** `restrict_scope(product-saas, scope_pred=single_tenant) = product-saas-single-tenant`. Used for UniversityC (the dashboard has exactly one customer org). Adds `H_K_extra = no_multi_tenant_isolation_required` and lets the solver relax tenant-isolation-related soft objectives.

### E.3 `compose(K_1, K_2) -> K_out`

**Intent.** Combine two profiles into a hybrid (covers v0 hybrids like LSD = content-pipeline + product-saas).

**Input.** Two K-profiles.

**Output.** A K-profile that satisfies both parents.

**Transformation rules.**

```
H_out = H_1 ∪ H_2          (union, never average; per v0 §K)
W_out = normalize_blend(W_1, W_2, alpha)
        where alpha is the mixture weight (default 0.5/0.5)
T_out = T_1 ∪ T_2
F_out = F_1 ∪ F_2
E_out = E_1 ∪ E_2
```

**Soundness condition.** `H_1 ∪ H_2` is satisfiable (no contradicting hard constraints). If it is not satisfiable, the compose fails and the operator must be replaced with explicit precedence rules.

**Worked example.** `compose(content-pipeline, product-saas) = LSD`. H_LSD = source-provenance ∪ audit-before-publish ∪ publish-cutoff ∪ RBAC-PII-isolation ∪ schema-migration-safety ∪ output-correctness. W_LSD blends c_derive/c_find/c_drift with c_modify/c_loss/c_find.

### E.4 `specialize_tenant(K_engine, tenant_id) -> K_tenant`

**Intent.** The inverse of `lift_tenant`. Given an engine-class K, produce the tenant-class K for a specific tenant.

**Input.** An engine K-profile plus a tenant identifier.

**Output.** A tenant-scoped K-profile.

**Transformation rules.**

```
H_out = H_engine
      \ {engine-only constraints: api_semver, no_tenant_data_at_rest}
      ∪ {tenant-specific hard constraints: tenant_id_pinned, end_user_consent_basis}

W_out = renormalize(
          W_engine
          with c_money weight restored to tenant defaults,
          with c_modify weight reduced (single-tenant blast radius)
        )

T_out = T_engine
      ∪ {tenant tools: SMTP, Stripe, end-user-auth}

F_out = F_engine
      ∪ {tenant fields: tenant_id, billing_state}

E_out = E_engine
      \ {tenant_data/*, tenant_secrets/*}   (now permitted in the tenant layer)
```

**Soundness condition.** `specialize_tenant ∘ lift_tenant = id` up to renaming of tenant_id. This is the LSP-style behavioral round-trip: lifting then specializing recovers the original tenant profile.

**Worked example.** `specialize_tenant(neural-gtm, "AgencyA") = outbound-pipeline_AgencyA`, where `outbound-pipeline_AgencyA` is the v0 outbound-pipeline plus AgencyA-specific manifest fields.

### E.5 Derivation graph for v0.2

Bootstrap (immutable):

```
outbound-pipeline, content-pipeline, product-marketing, product-saas,
research-memory, audit-pipeline, intel-pipeline
```

First derivations needed for the current Neural portfolio:

```
neural-gtm                 = lift_tenant(outbound-pipeline)
LSD                        = compose(content-pipeline, product-saas)
UniversityC                       = restrict_scope(product-saas, single_tenant)
sheetal-gs-engine          = compose(audit-pipeline, content-pipeline)
deskd-intel            = intel-pipeline                              (base, no derivation)
personal-twin              = compose(research-memory, intel-pipeline)
ClinicE                    = compose(product-saas, content-pipeline)
AgencyA                      = specialize_tenant(neural-gtm, "AgencyA")
                          ≡ outbound-pipeline                            (round-trip)
BrandB                     = product-marketing                          (base, no derivation)
```

This is the full lattice needed today. Eight projects, four base classes, four derivations.

## Part F - Simplicity Prior Recovery (Task 5)

### F.1 The risk

RQ8 established H_simp as a soft regularizer:

```
H_simp(A_M,x) =
  alpha_modify * c_modify(A_M,x)
  + alpha_drift * c_drift(A_M,x)
  + alpha_struct * structural_entropy(A_M,x)
  + alpha_rel * relation_count_penalty(A_M,x)
```

The alpha weights are calibrated **per K class**, taking W_K as the prior. In the fixed-taxonomy form, this works because W_K is in the registry. In the free-bag form, every folder must re-declare alphas, which means **either every folder uses the same defaults (defeating the point) or every folder uses different defaults (no prior at all)**. Either way, H_simp loses its calibration anchor.

### F.2 Recovery mechanism for the lattice form

In the lattice form, H_simp is **inherited along the derivation chain**, with adjustments at each operator:

- `lift_tenant(K)` shifts the simplicity prior toward c_modify and c_drift (engines change rarely; when they do, all tenants pay). New alphas:
  ```
  alpha_modify_lifted = alpha_modify_in * (1 + lift_amplification)
  alpha_drift_lifted  = alpha_drift_in  * (1 + lift_amplification)
  alpha_struct_lifted = alpha_struct_in
  alpha_rel_lifted    = alpha_rel_in
  ```
  with `lift_amplification = 1.5` as a v0.2 default.
- `restrict_scope(K, pred)` does not change H_simp alphas (specialization preserves the prior).
- `compose(K_1, K_2)` blends H_simp with the same mixture alpha as W_K.
- `specialize_tenant(K_engine, t)` is the inverse of lift_tenant: divide the amplification.

This gives every derived K-profile a **principled** H_simp prior without per-folder declarations.

### F.3 Recovery mechanism for the free-bag form (for the rejected option)

If we ever chose the free-bag form, the only viable recovery is a **schema default + learned-from-corpus prior**:

1. The folder manifest schema declares all five fields (H, W, T, F, E) as optional with a `prior_ref` that names a corpus-learned default profile.
2. A nightly job learns the prior from all observed folder manifests via a maximum-likelihood fit per cluster (k-means on the W vectors).
3. The solver uses the learned prior when a folder declares no values.

This works in principle but requires significantly more infrastructure (clustering, learning, monitoring) than the lattice approach. It is the right fallback if the lattice ever fails to derive a usable profile for some new project shape (see falsifiers in Part L).

## Part G - Empirical Fit: Per-Project Table (Task 6)

I sanity-checked the eight Neural projects by listing top-level layouts (AgencyA has `audits/ briefs/ catalog/ contracts/ leads/ scripts/ sequences/ voice/`; BrandB has `brand_twin/ creatives_analysis/ artisan_cloud/ db.sqlite3/ frontend/`; universityc-dashboard-app has `src/ docs/ playwright-report/ scripts/ RBAC_MOCKUP_*.html`; personal-twin has dozens of `MEMORY_V2_*.md`, `GRAPH_SCHEMA_DESIGN.md`; sheetal-gs-engine has `audit/ deals/ evidence/ feedback/ kb/ parsers/ rules/`; ClinicE has many `Phase_*.md`, `SARAH_*.md`, `TELEPHONY_*.md`; Longevity-Science-Daily has `web/ drafts/ quiz/ supabase/`; neural-gtm has just `waterfall/` with all the engine phase folders).

The fit per project under each form:

| Project | Top-level shape | Fixed taxonomy fit | Lattice derivation | Free-bag verdict |
|---|---|---|---|---|
| **AgencyA** | leads, sequences, contracts, voice; tenant-scoped outbound | outbound-pipeline (clean) | `specialize_tenant(neural-gtm, "AgencyA")` or base | clean but loses W_K prior |
| **BrandB** | brand_twin, creatives_analysis, shopify-to-sheets, sqlite | product-marketing (clean) | product-marketing (base) | clean but loses W_K prior |
| **UniversityC** | src, RBAC_MOCKUP_*.html, playwright, single client | product-saas (mostly; single-tenant is awkward) | `restrict_scope(product-saas, single_tenant)` (clean) | clean but loses W_K prior |
| **Personal Twin** | MEMORY_V2_*, GRAPH_SCHEMA, dozens of memory docs, intel briefings | research-memory (mostly; intel is extra) | `compose(research-memory, intel-pipeline)` (clean) | clean but loses W_K prior |
| **sheetal-gs-engine** | audit, deals, evidence, rules, rf_writer | audit-pipeline (mostly; rule-engine generates content) | `compose(audit-pipeline, content-pipeline)` (clean) | clean but loses W_K prior |
| **deskd-intel** | (sibling repo; per memory: PR_0001 schema, 6-layer pipeline, intel briefs) | intel-pipeline (clean) | intel-pipeline (base) | clean but loses W_K prior |
| **Longevity-Science-Daily** | web, drafts, quiz, supabase; both content publishing and SaaS surface | hybrid (no single class); v0 noted as 0.65 content + 0.35 saas | `compose(content-pipeline, product-saas)` (clean) | clean but loses W_K prior |
| **ClinicE** | Phase_*, SARAH_*, TELEPHONY_*; product-saas plus content pipeline | hybrid (no single class) | `compose(product-saas, content-pipeline)` (clean) | clean but loses W_K prior |
| **neural-gtm** (engine layer) | waterfall/ + phase_w0..phase_wv engine code | **no fit** (trigger for RQ9) | `lift_tenant(outbound-pipeline)` (clean) | clean but loses W_K prior |

**Summary.**
- Fixed taxonomy fits cleanly for **4 of 9** (AgencyA, BrandB, deskd-intel; arguably sheetal-gs-engine). Forces hybrids for **3 of 9** (LSD, ClinicE, Personal Twin). Forces an awkward restriction for **1 of 9** (UniversityC). **Fails outright for 1 of 9** (neural-gtm).
- Lattice fits cleanly for **9 of 9**, with derivations limited to one operator deep for 7 of 9 and two operators deep for none (composition counts as one operator).
- Free-bag fits cleanly for all 9 by definition, but loses the calibrated H_simp prior for all 9.

The empirical evidence is decisive: **the fixed taxonomy has a >50% misfit rate on the current portfolio**. The lattice fixes every misfit with at most one derivation. The free-bag form is over-expressive and pays a calibration tax everywhere.

## Part H - COP Encoding Impact per Form (Task 7)

The relevant baseline is `impl/a_star/solver/model.py` at lines 67-79:

```python
def build_model(
    facts: list[FolderFact],
    k_class: str = "outbound-pipeline",
) -> tuple[z3.Optimize, dict]:
    profile: KProfile = get_profile(k_class)
    opt = z3.Optimize()
    ...
```

The function takes K as a string, looks up KProfile from the registry, and uses `profile.soft_weights` at lines 140-188 to weight `opt.add_soft(...)`.

### H.1 Fixed taxonomy (v0 baseline)

```python
def build_model(facts, k_class: str = "outbound-pipeline"):
    profile = get_profile(k_class)              # dict lookup; O(1)
    ...
```

**Z3 model size.** Unchanged. ~5-6 hard constraints, ~10-12 soft constraints per folder (current AgencyA run produces ~70 folders -> ~700 soft clauses).

**Soft objective shape.** Unchanged: one weighted sum.

**Impact on growth.** Every new K-class requires editing `profiles/__init__.py` and shipping a new release.

### H.2 Inheritance lattice (recommended)

```python
def build_model(facts, k_expr: KExpr = KExpr.base("outbound-pipeline")):
    profile = materialize(k_expr)                # traverse lattice; O(depth)
    ...
```

Where `KExpr` is a small algebraic type:

```python
@dataclass(frozen=True)
class KExpr:
    op: Literal["base", "lift_tenant", "restrict_scope", "compose", "specialize_tenant"]
    args: tuple                                  # base name | (KExpr,) | (KExpr, pred) | (KExpr, KExpr) | (KExpr, tenant_id)

    @classmethod
    def base(cls, name: str) -> "KExpr":
        return cls("base", (name,))

def materialize(expr: KExpr) -> KProfile:
    if expr.op == "base":
        return get_profile(expr.args[0])
    if expr.op == "lift_tenant":
        return LIFT_TENANT(materialize(expr.args[0]))
    if expr.op == "restrict_scope":
        base, pred = expr.args
        return RESTRICT_SCOPE(materialize(base), pred)
    if expr.op == "compose":
        a, b = expr.args
        return COMPOSE(materialize(a), materialize(b))
    if expr.op == "specialize_tenant":
        engine, tenant = expr.args
        return SPECIALIZE_TENANT(materialize(engine), tenant)
```

**Z3 model size.** Same as fixed taxonomy. Materialization produces the same KProfile object the solver expects. The lattice lives in the **builder**, not in the Z3 model.

**Soft objective shape.** Same scalarized sum. The weights come from the materialized W_K.

**Impact on growth.** New K-profiles are produced by writing a derivation expression, not by editing the registry. The four operators stay constant.

**Caching opportunity.** `materialize` is pure; memoize by `KExpr` hash. The lattice depth in practice is 1-2 (see Part G), so the cache hit rate is high.

**API change for callers.** Either accept a `k_class: str` (backwards compat: parse "lift_tenant(outbound-pipeline)" as a derivation expression) or accept a `k_expr: KExpr` (cleaner; recommended for v0.2 once the migration completes). v0.2 ships both signatures and deprecates the string form over v0.3.

### H.3 Free constraint-bag (rejected option)

```python
def build_model(facts, manifest_path: str | None = None):
    if manifest_path:
        h, w, t, f, e = read_constraints_from_manifest(manifest_path)
    else:
        h, w, t, f, e = LEARNED_PRIOR
    ...
```

**Z3 model size.** Potentially explodes. Every folder may declare its own constraints, so the constraint count scales as O(folders × per-folder-constraints) rather than O(folders × W_K size). Estimated 3-5x larger model on a AgencyA-sized repo.

**Soft objective shape.** Either flat (one global sum) or per-folder (lots of small sums). Either way, the **calibration** is unclear because there is no shared prior to anchor weights.

**Impact on growth.** Maximum. Any new constraint can appear in any folder. But also: maximum risk of incoherence.

### H.4 Verdict

The lattice form costs roughly zero in solver time and small constant in builder code. The free-bag form costs both. The fixed form is fine for solver time but pays an editorial cost that we've already exceeded.

## Part I - Lifecycle Handling (Task 8)

A K-profile is not static. A project's profile evolves as the project grows. Three common patterns:

1. **Pure outbound becomes outbound + UI.** AgencyA started as a pure outbound pipeline; if we add a customer-facing dashboard, the K-profile should grow from outbound-pipeline to `compose(outbound-pipeline, product-saas)`.
2. **Content becomes content + RBAC.** LSD is already at `compose(content-pipeline, product-saas)`; if a paid subscription tier with seat management is added, the product-saas component dominates and we may want `compose(compose(content-pipeline, product-saas), product-marketing)` to capture the spend optimization.
3. **Tenant becomes engine.** AgencyA was a single repo; v0.1 split it into neural-gtm engine + AgencyA tenant. The engine is `lift_tenant(outbound-pipeline)`; AgencyA is the residual tenant.

Each form handles lifecycle differently:

| Form | Lifecycle handling |
|---|---|
| **Fixed taxonomy** | Re-classify. Pick a new class name (8th, 9th, ...). Risk: class name drift; risk that no available class fits. |
| **Inheritance lattice** | Re-derive. The new profile is a new derivation expression over the same base classes. The history is captured in the expression itself (a derivation chain serves as a changelog). Most natural form. |
| **Free constraint-bag** | Mutate the bag. Edit the manifest. Lose history unless we version manifests separately. |

The lattice form is the **only** one where lifecycle evolution is a structural operation rather than an editorial one. This is the third independent reason to prefer it.

## Part J - Recommendation: Formal v0.2 Redefinition of K (Task 9)

**Replace the v0 sentence:**

> "K is one of seven named classes: outbound-pipeline, content-pipeline, product-marketing, product-saas, research-memory, audit-pipeline, intel-pipeline."

**With:**

> **K is an element of the inheritance lattice `L_K` generated by seven bootstrap base classes (the v0 seven: outbound-pipeline, content-pipeline, product-marketing, product-saas, research-memory, audit-pipeline, intel-pipeline) under four formal operators (lift_tenant, restrict_scope, compose, specialize_tenant). Every K in `L_K` is either a base class or a derivation expression of bounded depth (default depth ≤ 3) over the base classes. The materialization function `materialize: KExpr -> KProfile` resolves any K to a concrete `(H_K, W_K, T_K, F_K, E_K)` tuple by traversing the derivation expression. The four operators are defined by the transformation rules in Part E of RQ9. Every derived K must satisfy the well-formedness condition `WF(K)` and the operator-specific soundness condition. The simplicity prior H_simp inherits along the derivation chain per the rules in Part F.5 of RQ9. Newly derived K-profiles enter production solver runs only after a one-time engineering review verifies WF(K) and soundness.**

**Implementation diff against `impl/a_star/solver/model.py`:**

1. Introduce `KExpr` dataclass in `impl/a_star/profiles/expressions.py`.
2. Implement `materialize(expr: KExpr) -> KProfile` plus the four operator functions (LIFT_TENANT, RESTRICT_SCOPE, COMPOSE, SPECIALIZE_TENANT).
3. Extend `build_model` signature to accept `KExpr | str`, with the string form parsed as either a base name or a derivation expression in a small s-expression syntax.
4. Cache `materialize` by `KExpr` hash.
5. Add a `validate_kexpr(expr)` that checks WF and soundness; called once per CI run, not per solve.

**Migration plan.**

- v0.1 fixed taxonomy is **bytewise-compatible** with v0.2: every v0 class name resolves to a 0-step derivation expression. No existing call site breaks.
- v0.1 callers using `build_model(..., k_class="outbound-pipeline")` continue to work.
- New callers use `build_model(..., k_expr=KExpr("lift_tenant", (KExpr.base("outbound-pipeline"),)))` or the string form `"lift_tenant(outbound-pipeline)"`.

**What stays frozen.**

- The seven base classes (their H, W, T, F, E tuples) stay frozen as v0 defined them.
- The four operators stay frozen. New operators require a v0.3 release.
- The simplicity-prior inheritance rules in Part F.5 stay frozen.

**What grows.**

- The derivation graph grows freely as new projects appear.

## Part K - Falsifiers (Task 10)

Under the recommended form, the following observations would force a revision:

1. **A project that fits no derivation chain of depth ≤ 3 from the seven bootstrap classes.** For example, a hardware-firmware project, a regulated-clinical-trial pipeline, or a cryptocurrency-custody system. The first would force an 8th bootstrap class; the second and third would force at least one new operator. If this happens within the next 6 months of Neural growth, the lattice has under-specified its base.
2. **A derivation that requires an operator outside the four.** For example, `temporal_specialize(K, time_window)` to model "this K applies only during business hours" or `geographic_specialize(K, region)` to model regulatory scope. If we cannot express such cases via `restrict_scope` with a richer predicate language, we need a 5th operator.
3. **`compose(K_1, K_2)` produces an unsatisfiable `H_1 ∪ H_2` for a real project pair.** This would mean some K classes have incompatible hard constraints and cannot be combined. The current v0 catalog should be safe (the v0 §K note explicitly says "union hard constraints (never average)" works for the LSD = 0.65 content + 0.35 saas case), but a real failure would force a precedence operator or a constraint-relaxation operator.
4. **`specialize_tenant ∘ lift_tenant ≠ id` on real data.** If the round-trip loses information (which it can, in our current spec, because `lift_tenant` discards H constraints), then `lift_tenant` is destructive and the lattice is not a true lattice. The mitigation is to make `lift_tenant` archival (preserve dropped constraints in a side channel) at the cost of slightly larger profiles.
5. **The free-bag form turns out to be necessary for a single project.** If one project genuinely requires per-folder constraint declarations that cannot be expressed as a single K-profile (perhaps a megarepo with truly heterogeneous subprojects), then the lattice is insufficient and we must support both forms (lattice for the top-level K, free-bag at folder level inside that K). v0.2 leaves the door open for this by treating the folder manifest schema as orthogonal to K.
6. **Solver runs take significantly longer with materialized derived profiles.** If `materialize` introduces non-trivial overhead (>10% of solve time) on AgencyA-scale repos, the cache is insufficient and we may need to pre-materialize and persist derived profiles.
7. **The simplicity-prior inheritance produces miscalibrated weights for a real derived profile.** If `lift_amplification = 1.5` (Part F.5) drives c_modify weights so high that the engine becomes effectively frozen, we have over-corrected. Calibrate from observed cost deltas (which is the RQ12 measurement plan output).
8. **Engineering review of derived K-profiles becomes a bottleneck.** If more than one new derivation per week needs review, the operator is too tight; if zero need review per quarter, the operator is too loose. Target one review per month at steady state.

If any of (1)-(4) occur, K is misformulated and v0.3 must revisit. If (5)-(8) occur, K is formulated correctly but the surrounding mechanism needs tuning.

## Bibliography

### Biology and library science taxonomy
- [Cladistics - New World Encyclopedia](https://www.newworldencyclopedia.org/entry/Cladistics)
- [Incompatibility of Cladistic and Linnaean Systems - Palaeos](http://palaeos.com/systematics/taxonomy/incompatible.html)
- [Using trees for classification - UC Berkeley Understanding Evolution](https://evolution.berkeley.edu/phylogenetic-systematics/using-trees-for-classification/)
- [Faceted classification - Wikipedia](https://en.wikipedia.org/wiki/Faceted_classification)
- [Ranganathan's PMEST: The Foundation of Faceted Classification - LIS Education Network](https://www.lisedunetwork.com/ranganathans-pmest-the-foundation-of-faceted-classification/)
- [Fundamental categories: facets and facet analysis - INFLIBNET](https://ebooks.inflibnet.ac.in/lisp2/chapter/fundamental-categories-facets-and-facet-analysis-principles-of-facet-sequence-or-citation-order/)
- [Comparison of Dewey and Library of Congress subject classification - Wikipedia](https://en.wikipedia.org/wiki/Comparison_of_Dewey_and_Library_of_Congress_subject_classification)
- [Library of Congress Classification - Wikipedia](https://en.wikipedia.org/wiki/Library_of_Congress_Classification)
- [We Need to Radically Rethink the Library of Congress Classification - LitHub](https://lithub.com/we-need-to-radically-rethink-the-library-of-congress-classification/)

### Ontology engineering and type theory
- [What are OWL Ontologies? - U. Washington (Bill Howe CS410)](https://homes.cs.washington.edu/~billhowe/cs410/owl_overview.pdf)
- [The Open World Assumption Considered Harmful - Douroucouli](https://douroucouli.wordpress.com/2020/09/04/the-open-world-assumption-considered-harmful/)
- [The Open World Assumption: Elephant in the Room - M. Bergman](https://www.mkbergman.com/852/the-open-world-assumption-elephant-in-the-room/)
- [Disjointness, open and local closed world reasoning - Owlready2 docs](https://owlready2.readthedocs.io/en/latest/disjoint.html)
- [Wadler & Blott, How to Make Ad-Hoc Polymorphism Less Ad Hoc, POPL 1989 (ACM DL)](https://dl.acm.org/doi/pdf/10.1145/75277.75283)
- [Type class - Wikipedia](https://en.wikipedia.org/wiki/Type_class)
- [Type Systems: Structural vs. Nominal Typing Explained - Jamie Kyle](https://medium.com/@thejameskyle/type-systems-structural-vs-nominal-typing-explained-56511dd969f4)
- [An Overview of Nominal-Typing versus Structural-Typing in OOP - arXiv 1309.2348](https://arxiv.org/pdf/1309.2348)
- [Liskov substitution principle - Wikipedia](https://en.wikipedia.org/wiki/Liskov_substitution_principle)
- [A Better Explanation of the Liskov Substitution Principle - Hillel Wayne](https://www.hillelwayne.com/post/lsp/)

### Architecture pattern catalogs
- [Design Patterns - Wikipedia (GoF criticism)](https://en.wikipedia.org/wiki/Design_Patterns)
- [The Gang of Four Gave Us 23 Design Patterns - Are They Still Relevant? - Medium](https://medium.com/@freddy.dordoni/the-gang-of-four-gave-us-23-design-patterns-are-they-still-relevant-in-2025-f2e999c384c0)
- [Research state of the art on GoF design patterns - ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0164121213000757)
- [Pattern-oriented software architecture (POSA) - ResearchGate](https://www.researchgate.net/publication/228722744_Pattern-oriented_software_architecture)
- [Bounded Context - Martin Fowler](https://www.martinfowler.com/bliki/BoundedContext.html)
- [Domain-driven design - Wikipedia](https://en.wikipedia.org/wiki/Domain-driven_design)
- [Strategic Domain Driven Design with Context Mapping - InfoQ](https://www.infoq.com/articles/ddd-contextmapping/)
- [Microservices Patterns (Manning) - Chris Richardson](https://www.manning.com/books/microservices-patterns)
- [microservices.io patterns catalog](https://microservices.io/patterns/)
- [Data Mesh Principles and Logical Architecture - Martin Fowler / Zhamak Dehghani](https://martinfowler.com/articles/data-mesh-principles.html)
- [Data Mesh Principles and Logical Architecture Defined - InfoQ](https://www.infoq.com/news/2020/12/data-mesh-architecture/)
- [Data Mesh: a Systematic Gray Literature Review - arXiv 2304.01062](https://arxiv.org/pdf/2304.01062)

### Modularity and decomposition
- [On the Criteria To Be Used in Decomposing Systems into Modules - D. L. Parnas, 1972 (MIT mirror)](http://sunnyday.mit.edu/16.355/parnas-criteria.html)
- [On the criteria to be used in decomposing systems into modules - the morning paper](https://blog.acolyer.org/2016/09/05/on-the-criteria-to-be-used-in-decomposing-systems-into-modules/)
- [On the criteria to be used in decomposing systems into modules - Communications of the ACM](https://dl.acm.org/doi/10.1145/361598.361623)

### Feature modeling and software product lines
- [Feature-Oriented Domain Analysis (FODA) Feasibility Study - CMU SEI, Kang et al. 1990](https://www.sei.cmu.edu/library/feature-oriented-domain-analysis-foda-feasibility-study/)
- [Feature-oriented domain analysis - Wikipedia](https://en.wikipedia.org/wiki/Feature-oriented_domain_analysis)
- [Feature model - Wikipedia](https://en.wikipedia.org/wiki/Feature_model)
- [A formal framework for software product lines - ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0950584913001262)
- [Semantics of FODA feature diagrams - Academia.edu](https://www.academia.edu/829451/Semantics_of_FODA_feature_diagrams)

### Constraint modeling
- [MiniZinc Handbook 2.9.5](https://docs.minizinc.dev/en/latest/)
- [MiniZinc - Wikipedia](https://en.wikipedia.org/wiki/MiniZinc)
- [MiniZinc Constraint Modeling Language - Emergent Mind](https://www.emergentmind.com/topics/minizinc-constraint-modeling-language)
- [Global constraints - MiniZinc Handbook](https://www.minizinc.org/doc-2.5.0/en/lib-globals.html)

### Configuration management and policy as code
- [Understanding Ansible, Terraform, Puppet, Chef and Salt - RedHat](https://www.redhat.com/en/topics/automation/understanding-ansible-vs-terraform-puppet-chef-and-salt)
- [Chef vs Puppet vs Ansible - Veritis](https://www.veritis.com/blog/chef-vs-puppet-vs-ansible-comparison-of-devops-management-tools/)
- [Ansible vs. Puppet vs. Chef - IPSpecialist Medium](https://ip-specialist.medium.com/ansible-vs-puppet-vs-chef-a5fbee6ff4a9)
- [OPA Policy Language docs](https://www.openpolicyagent.org/docs/policy-language)
- [Open Policy Agent (OPA) docs](https://www.openpolicyagent.org/docs)
- [Introducing Policy as Code: OPA - CNCF](https://www.cncf.io/blog/2020/08/13/introducing-policy-as-code-the-open-policy-agent-opa/)
- [Cedar Policy Language reference](https://docs.cedarpolicy.com/)
- [Cedar Entities](https://docs.cedarpolicy.com/policies/syntax-entity.html)
- [Cedar Schema overview](https://docs.cedarpolicy.com/schema/schema.html)
- [Cedar: A New Language for Expressive, Fast, Safe, and Analyzable Authorization - Amazon Science PDF](https://assets.amazon.science/96/a8/1b427993481cbdf0ef2c8ca6db85/cedar-a-new-language-for-expressive-fast-safe-and-analyzable-authorization.pdf)

### Effects and modular composition (supporting algebraic-effects pattern for compose operator)
- [Handling Polymorphic Algebraic Effects - Springer](https://link.springer.com/chapter/10.1007/978-3-030-17184-1_13)
- [A Calculus for Scoped Effects & Handlers - arXiv 2304.09697](https://arxiv.org/abs/2304.09697)

---

*Memo prepared 2026-05-24. Claude Code native deep-search (WebSearch + WebFetch). Replaces the cancelled Parallel.ai ultra2x run for RQ9. To be paired with RQ10 (seam-as-primitive) and RQ12 (seam-cost) when those threads complete in this wave.*
