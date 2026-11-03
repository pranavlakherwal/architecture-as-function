# A* Bibliography

Annotated citations grouped by research question. Full source list lives in each `research/wave{N}/RQ*_raw.json`.

## RQ1 — Effective rank of `C`

- **DORA** (Forsgren, Humble, Kim) — *Accelerate*. Four key metrics cluster into 2 latent factors (throughput, stability). Evidence for c_modify/c_drift/c_loss collinearity.
- **SPACE** (Forsgren, Storey, Maddila, Zimmermann, Houck, Butler, 2021, *ACM Queue*). 5 dimensions of developer productivity. Justifies splitting c_onboard out of architecture-intrinsic cost.
- **COCOMO II** (Boehm et al.) — software cost dimensions known to be correlated.
- **OAIS / PREMIS** — archival cost structure: storage, ingest, access, preservation planning.
- **FAIR v3.0** — annualized loss expectancy; basis for c_loss measurement.
- **Hick-Hyman law** — cognitive cost of choice; relevant to c_find.

## RQ2 — Functional form (COP vs CSP vs continuous)

- **de Moura & Bjørner (2008)** — Z3: An Efficient SMT Solver. CAV 2008.
- **Bjørner, Phan, Fleckenstein (2015)** — νZ: An Optimizing SMT Solver. TACAS 2015.
- **Z3 Optimize API** — soft constraints, lexicographic/Pareto/box objective modes.
- **NSGA-II** (Deb et al., 2002) — multi-objective evolutionary baseline.
- **FastSMT** (Balunović et al., 2018) — learned heuristics for SMT, ~100× speedup. v1 path.
- **MaxSAT** and weighted CSP literature — soft-constraint framing baseline.

## RQ3 — Per-axis measurement

- **Sinha (2023)** — code search task instrumentation for c_find.
- **Mannan et al.** — structural entropy for c_drift.
- **Microsoft DevEx research** (Noda, Storey et al., 2023) — feedback loops, cognitive load, flow.
- **GitHub Octoverse / public-repo studies** — passive-from-git proxies.
- **FAIR v3.0** — c_loss measurement procedure.
- **OAIS** — c_storage tiering economics.

## RQ4 — K taxonomy

- **Bass, Clements, Kazman** — *Software Architecture in Practice*. Quality attributes.
- **SEI ATAM** — Method for architecture evaluation; scenarios, risks, sensitivity points.
- **Rozanski & Woods** — *Software Systems Architecture*. Viewpoints + perspectives.
- **Evans (2003)** — *Domain-Driven Design*. Bounded contexts.
- **Vernon** — *Implementing Domain-Driven Design*.
- **Fowler** — Bounded Context (bliki).
- **Rosenfeld & Morville** — *Information Architecture for the World Wide Web*. Organization schemes.
- **Forte** — *Building a Second Brain* (PARA).
- **Ahrens** — *How to Take Smart Notes* (Zettelkasten).
- **Procida** — Diataxis.
- **Google MLOps levels** — manual / pipeline / CI-CD automation.
- **Databricks Medallion** — Bronze/Silver/Gold.
- **Lambda + Kappa architectures** — batch vs stream.
- **AI Agent Systems survey (arXiv 2601.01743)** — agent components, traceability.

## RQ5 — Folder-as-ontology

- **W3C OWL** — formal ontology language.
- **W3C RDF** — graph data model.
- **Schema.org** — 45M+ domains, 450B+ marked-up objects.
- **JSON Schema, OpenAPI** — machine-readable contracts.
- **Bergman, Whittaker, Falk et al.** — *Folder vs Tag Preference in PIM*. Strong folder preference (~90% folder use).
- **Whittaker, Matthews, Cerruti, Badenes, Tang (CHI 2011)** — *Am I Wasting My Time Organizing Email?* 345 users, 85k refinding actions. Search/threading > preparatory filing in email.
- **Voit, Andrews, Slany** — *Tagging Might Not Be Slower Than Filing in Folders*. TagTrees.
- **Barreau & Nardi (1995)** — *Finding and Reminding*.
- **Benn et al.** — fMRI study, folder navigation uses spatial brain regions.
- **English, Hearst, Sinha, Swearingen, Yee (Flamenco)** — hierarchical faceted metadata.
- **Golder & Huberman** — Usage Patterns of Collaborative Tagging Systems.
- **Ranganathan** — Colon Classification, PMEST facets.
- **Boardman, Spence, Sasse** — Too Many Hierarchies?
- **Carlini et al.** — Extracting Training Data from LLMs.

## RQ6 — Resilience + creativity + c_onboard + c_reverse reclassification

- **Hollnagel** — *Safety I and Safety II*; Resilience Assessment Grid (4 potentials: respond/monitor/learn/anticipate).
- **Woods** — Theory of Graceful Extensibility.
- **Cook** — *How Complex Systems Fail*.
- **Taleb** — *Antifragile*. Robust ≠ resilient ≠ antifragile.
- **Google SRE Book** — SLI, SLO, error budget.
- **Rosenthal et al.** — *Chaos Engineering*; Principles of Chaos.
- **Cross** — *Designerly Ways of Knowing*; *Design Thinking*.
- **Alexander** — *Notes on the Synthesis of Form*; *A Pattern Language*; *The Timeless Way of Building*.
- **Shah, Smith, Vargas-Hernandez** — Assessing Design Creativity (novelty + usefulness).
- **DORA Failed Deployment Recovery Time** — operational metric, not pure architecture.
- **Git Undoing Things** docs; **PostgreSQL ROLLBACK**; **Statsig**; **LaunchDarkly** — tooling-side reverse cost.

## RQ7 — Deletion-irreversibility and archival policy

- **GDPR Article 17** (EUR-Lex) — right to erasure + Article 17(3) exceptions.
- **EDPB Recommendations 01/2020** — supplementary measures (Schrems II).
- **ICO** Anonymisation + Right to Erasure guidance.
- **CCPA / CPRA** — Cal. Civ. Code 1798.105.
- **HHS HIPAA PHI Disposal FAQ**.
- **PCI DSS v4.0.1 Requirement 3.2.1** — account data minimization; verification every 3 months.
- **17 CFR 210.2-06** — SEC 7-year audit retention.
- **SEC Final Rule 33-8180** — retention discourages destruction.
- **ISO 15489-1:2016** — records management.
- **ISO/TS 7538:2024** — disposition.
- **DoD 5015.02** — records management requirements.
- **MoReq2010** — disposal schedules + holds + residual records.
- **OAIS / ISO 14721** — preservation, authorized disposition.
- **PREMIS** — preservation events (deletion, redaction, deaccession).
- **NIST SP 800-88 Rev. 2** — Clear/Purge/Destroy + Certificate of Sanitization.
- **Kafka Log Compaction docs** — tombstones, delete.retention.ms.
- **CRDT Study** — tombstone garbage collection.
- **ClickHouse TTL**; **PostgreSQL Routine Vacuuming**.
- **Kurrent / EventStore** — soft vs hard delete patterns.
- **Restic Forget / Prune** — separation of intent and reclaim.
- **S3 Object Lock, Glacier Vault Lock** — WORM.
- **Google Cloud Storage soft delete** — 7-day default.
- **GitHub Secret Scanning** — Git history scanned across all branches.
- **Carlini et al.** — Extracting Training Data from LLMs (training-data memorization).

## RQ8 — S(M,T)↔A* mapping + primitive operations

- **Z3 Optimize** — soft constraints, weighted soft, lex/Pareto/box objective modes.
- **MDL** (Rissanen) — minimum description length.
- **Solomonoff** — algorithmic prior, Occam.
- **Burnham & Anderson** — *Model Selection and Multimodel Inference* (AIC/BIC).
- **Srivastava, Hinton et al. (2014)** — Dropout (JMLR). Analogical regularization.
- **Parnas (1972)** — On the Criteria To Be Used in Decomposing Systems Into Modules.
- **SEI Quality Model** — modifiability, testability, deployability, availability, performance.
- **Gamma, Helm, Johnson, Vlissides** — *Design Patterns*. 23 patterns.
- **Fowler** — Refactoring Catalog (online).
- **Mens & Tourwé (2004)** — *A Survey of Software Refactoring*.
- **Alembic Operations docs**; **Django Migration Operations**; **Prisma Down Migrations**; **Liquibase Rollback**; **Flyway Migrations** — convergent migration-tool patterns.
- **Git mv** — move/rename as one operation family.
- **PARA Method** — 4 top-level knowledge categories.
- **Zettelkasten Note Types** — fleeting/literature/permanent/project.
- **IBM Database Normalization**; **Denormalization** (DataCamp).
- **Databricks Medallion Architecture** — 3-layer refinement.
- **Stojanovic & Motik** — Ontology Evolution.
- **Klein & Noy** — Ontology Versioning: logs / diffs / minimal transformation sets.

## Foundational lineage and adversarial neighbors (added 2026-06-06, the look-back)

These were missing and they reshape the novelty claim. Cite them; lead with the threats.

- **Suh, Nam P. (1990, *The Principles of Design*; 2001, *Axiomatic Design*).** A*(I, L, K, T) → (A, D) is structurally Axiomatic Design: map functional requirements to design parameters. His **Independence Axiom** (keep functional requirements decoupled) is our IC3 seam logic and the engine/tenant split; his **Information Axiom** (minimize information content) is our H_simp / MDL prior. Honest consequence: A* did not invent the framing. The defensible novelty narrows to "a calibrated cost model plus an SMT encoding." State it that way.
- **MacCormack, Rusnak & Baldwin (2006), *Exploring the Structure of Complex Software Designs* (Design Structure Matrices, propagation cost).** The redundancy threat to the headline equation: propagation cost already measures how change propagates as coupling grows, on real codebases, with human-replicable metrics. Test whether propagation cost predicts modification cost better than α·√N. If it does, the modification law is not just under-evidenced, it is redundant. Lead with this.
- **Baldwin & Clark (2000), *Design Rules: The Power of Modularity*.** Modular operators and **Net Option Value**. NOV is the principled "when does a seam pay off" formalism, stronger than our hand-set R1/R2/R3 thresholds.
- **Harman & Jones (2001); Harman (2007) — Search-Based Software Engineering.** The umbrella the A* framing sits inside (architecture as optimization / design-space search). Cite for legitimacy and for the NSGA-II vs Z3 question.
- **Lehman (1980), Laws of Software Evolution.** The Second Law (a system's complexity increases unless work is spent reducing it) flags that c_drift ≈ 1/N and c_loss ≈ 1/N may be sign-wrong. Mark them "hypothesized, sign unverified."
- (Already cited and relevant: Parnas 1972 on decomposition, Burnham & Anderson on AIC/BIC, Rissanen MDL. The free-power N^p refit, RQ14, uses the AIC/BIC machinery already in RQ8.)

---

*Format: full URLs and source quality notes per RQ are preserved in `protocols/wave{N}_state.json` and `research/wave{N}/RQ*_raw.json`.*
