# Constraint-First Optimization for A* Architecture Decisions

## Executive Summary

- **Hybrid COP/MaxSAT Fits A***: Z3 Optimize supports hard constraints via assert and soft objectives via assert-soft with lexicographic, Pareto, or box priorities Introduction | Online Z3 Guide [40] -> Use a hybrid Constraint Optimization Problem (COP) with MaxSMT in v0.
- **Hard-Constraint Guarantees Are Non-Negotiable**: SMT/MaxSMT natively enforces integrity constraints and can surface unsat cores for debugging Z3 - Microsoft Research [19] -> Model single-source-of-truth, archival reversibility, and ontology coherence as hard assertions.
- **Multi-Objective Handling Is Built-In**: Z3 supports lexicographic, Pareto, and box modes for multiple objectives; weights on assert-soft map cleanly to preferences Introduction | Online Z3 Guide [40] -> Start lexicographic; optionally enumerate Pareto slices for operator review.
- **Discrete Decisions Require Symbolic Reasoning**: Evolutionary MOEAs used in software architecture discard infeasible mutations to enforce constraints Interactive Multi-Objective Evolutionary Optimization of Software Architectures [12] -> Avoid purely continuous or heuristic-first approaches for v0; keep them as adjuncts.
- **Interpretability Favors Constraint-Based**: Ontology+CSP integration shows how hierarchical structure and rules explain choices, with arc-consistency filtering and compatibility tables Integration of Ontologies and CSP for Product Configuration [63] -> Expose which constraints bind and which soft clauses drive the selected shape.
- **ILP Works for Quantitative Subproblems**: A MILP model for multi-cloud deployment achieved 50% optimization time reduction and 37% cost reduction vs. heuristics A MILP Approach for Multi-Cloud Capacity Allocation [58] -> Use ILP as a sidecar for numeric routing or capacity sub-decisions.
- **Solver Maturity Is High at Our Scale**: MiniZinc targets multiple backends (Gecode, Chuffed, OR-Tools, HiGHS, CPLEX, Gurobi) and Z3 is production-grade MiniZinc Solvers [38] Z3 - Microsoft Research [19] -> Expect sub-second to minutes at 5-200 primitives.
- **Learning-Guided Solving Is a v1 Upgrade**: FastSMT reports up to 100x speedups on Z3 by learning strategies on domain formulas FastSMT [25] -> Plan to learn solver strategies from A* logs if latency becomes a bottleneck.
- **Closest Adjacent Applications Confirm Feasibility**: MaxSAT-based product (re-)configuration and industrial feature-model SAT evaluations demonstrate viability for discrete configuration problems ReMax Product Re-Configurator [26] Industrial Feature-Model SAT Evaluation [41] -> Adopt config-style modeling of architecture primitives and constraints.
- **Gap: Direct Folder Hierarchy Optimization**: No paper optimizes folder/naming/persistence end-to-end; ontology and configuration work are adjacent Integration of Ontologies and CSP [63] -> Prototype on AgencyA and refine objectives and soft constraints empirically.

## Family 1: Continuous Optimization - Mature Multi-Objective Tooling, Weak Discrete Guarantee

Observation. Continuous and metaheuristic methods cast design as multi-objective optimization, seeking Pareto frontiers over conflicting quality metrics. Ramirez et al. encode architectures from UML class diagrams and use an interactive MOEA (compared against NSGA-II) to optimize metrics such as ICD, ERP, and GCR; feasibility is preserved by discarding or repairing infeasible mutations Interactive Multi-Objective Evolutionary Optimization of Software Architectures [12]. In deployment and capacity planning, MILP can encode queuing-based constraints and delivers significant speed and cost improvements versus heuristics A MILP Approach for Multi-Cloud Capacity Allocation [58].

Mechanism. MOEAs (NSGA-II, MOEA/D) provide native Pareto exploration and interactive steering but treat hard constraints indirectly, via penalty terms, repair operators, or feasibility-preserving encodings. Classical mathematical programming handles constraints exactly when the structure matches linear or convex forms, but many architecture decisions are discrete and symbolic, pushing models toward MIP with big-M or logical encodings.

Implications. For A*, where hard integrity rules must not be violated and outputs are symbolic structures, a continuous-first approach risks silent constraint violations unless wrapped in feasibility repairs or coupled with a symbolic constraint layer. It does, however, shine where quantitative subproblems dominate (e.g., capacity, latency budgets) and for generating interpretable Pareto frontiers for human trade-off.

- Typical formulations: MOEA over discrete encodings; MILP over linearized quantities; RL over learned policies for design actions Interactive MOEA Software Architectures [12] A MILP Approach [58].
- Maturity: High in engineering; NSGA-II widely surveyed; commercial solvers Gurobi/CPLEX and open-source HiGHS mature for LP/MIP HiGHS [61].
- Complexity: NP-hard in general for MIP; MOEAs are heuristic with no optimality guarantee; practical at our scale with careful modeling.
- Interpretability: Pareto plots and metric attributions help; no proof traces for hard infeasibility.
- Incremental tuning: Retune weights or constraints often requires re-solving; RL retraining is heavier.
- Adding constraints: Generally requires model refactoring or re-derivation of penalties/encodings.

Case study. Ramirez et al. show iMOEA discovers component partitions with human-in-the-loop preferences but enforces constraints by rejecting unfeasible individuals, not by native proof obligations Interactive MOEA Software Architectures [12]. This makes it a useful exploration aid, not a validator of integrity rules.

Strongest FOR. Best native handling and visualization of multi-objective trade-offs across many candidate structures NSGA-II Survey [15].

Strongest AGAINST. Cannot guarantee hard constraints without auxiliary mechanisms; discrete symbolic structure is awkward for pure continuous formulations Interactive MOEA Software Architectures [12].

## Family 2: Constraint Satisfaction - Native Hard Guarantees, Limited Optimization

Observation. CSP, SAT/SMT, and ASP encode variables over finite domains with logical constraints. SMT extends SAT with background theories (arithmetic, sets), allowing precise statements about structure and quantities. Systems such as Z3 and cvc5 are industrial-strength; MiniZinc offers a modeling layer targeting CP/MIP/SAT backends; clingo provides ASP with optimization statements Z3 - Microsoft Research [19] MiniZinc Solvers [38] Potassco Clingo [44].

Mechanism. Hard constraints are first-class; solvers produce models or unsat cores explaining conflicts. Multi-objective optimization is not native in plain SAT/SMT but can be layered: MaxSMT with weighted soft constraints, lexicographic priorities, or external iterative schemes. In knowledge organization, ontologies (hierarchies, types) integrate with CSP to turn concept rules and compatibility tables into enforceable constraints with arc-consistency filtering Integration of Ontologies and CSP [63].

Implications. For A*, mapping integrity rules to assertions yields hard guarantees and explanations for infeasibility. Objectives can be scalarized or handled via MaxSMT in Z3 Optimize. The approach is compositional: adding a new rule means adding a new assertion. This supports operator trust and day-2 evolvability.

- Typical formulations: SAT encodings, SMT over arithmetic and sets, ASP rules, CP models with global constraints.
- Maturity: High; Z3 widely used across software tooling; MiniZinc targets Gecode, Chuffed, OR-Tools, HiGHS, CPLEX, Gurobi Z3 - Microsoft Research [19] MiniZinc Solvers [38].
- Complexity: NP-complete in theory; very practical at 5-200 primitives; industrial feature-model analyses confirm scalability Industrial Feature-Model SAT Evaluation [41].
- Interpretability: Unsat cores, minimal explanations; constraint names serve as rationale.
- Incremental tuning: Add conjuncts, adjust soft-constraint weights; supports multi-shot solving.
- Adding constraints: Purely additive; no re-derivation of encodings needed.

Case study. Amini et al. integrate Protégé ontologies and CSP by mapping properties to variables and compatibility tables to SWRL rules, then enforcing arc-consistency to filter domains. Ontology captures hierarchy; CSP captures admissible combinations Integration of Ontologies and CSP [63].

Strongest FOR. Native hard-constraint enforcement and explanations build operator trust Z3 - Microsoft Research [19].

Strongest AGAINST. Multi-objective optimization is add-on; without MaxSMT/Optimize layers, support is limited.

## Family 3: Hybrid Constraint Optimization - Hard Constraints Meet Objective Minimization

Observation. Hybrid methods combine CSP/SMT for feasibility with optimization layers for preferences: COP extends CSP by adding an objective function; MaxSAT/MaxSMT introduce soft clauses with weights; MIP handles numeric substructures. Z3 Optimize unifies these by letting users assert hard constraints, assert-soft weighted preferences, and choose lexicographic, Pareto, or box aggregation Introduction | Online Z3 Guide [40] Objective Functions in Z3 [50].

Mechanism. In Z3, assert encodes hard constraints; assert-soft encodes soft clauses with optional weights and group IDs; the Optimize module drives lexicographic or Pareto search. Under the hood, Z3 blends Simplex for arithmetic with MaxSAT engines such as Fu-Malik (unweighted) and WPM2/HSMAX (weighted) Objective Functions in Z3 [50]. COP models in MiniZinc compile to FlatZinc for CP/MIP backends (Gecode, Chuffed, OR-Tools, HiGHS, CPLEX, Gurobi) MiniZinc Solvers [38]. MaxSAT has been used in re-configuration to minimize the number of changes while re-enabling feasibility ReMax Product Re-Configurator [26]. Recent IJCAI work advances weighted partial MaxSAT solvers CASHWMaxSAT, IJCAI 2025 [6].

Implications. For A*, encode integrity requirements as hard SMT constraints; express the 9D cost as soft objectives with weights or priorities; let the solver find feasible, minimally violating shapes with explanations. This yields both guarantees and actionable trade-offs.

- Typical formulations: COP with hard feasibility and soft cost; weighted partial MaxSAT; MIP sidecar for numeric routing.
- Maturity: High and improving; Z3 Optimize is stable; MiniZinc bridges to multiple solvers; MaxSAT solvers continue to improve Introduction | Online Z3 Guide [40] MiniZinc Solvers [38] CASHWMaxSAT, IJCAI 2025 [6].
- Complexity: NP-hard in general; practical for small to medium instances; strong pruning from constraints.
- Interpretability: Clear separation of must vs. prefer; unsat cores and objective contributions support explanations.
- Incremental tuning: Adjust weights, add soft clauses, or promote soft to hard without re-encoding core model.
- Adding constraints: Add new assert; side-effect confined to feasible set search.

Strongest FOR. Unifies hard guarantees with principled multi-objective optimization in one workflow Introduction | Online Z3 Guide [40].

Strongest AGAINST. Interactions between soft weights and hard constraints can be subtle; requires disciplined modeling and debugging.

## Published Applications to Architecture and Knowledge Organization

- Continuous optimization. Ramirez et al. demonstrate interactive MOEA-based discovery of component architectures from UML, balancing ICD, ERP, and GCR; constraints are enforced by feasibility-preserving mutation or rejection Interactive Multi-Objective Evolutionary Optimization of Software Architectures [12]. Ciavotta et al. formulate multi-cloud deployment as a queuing-theory-based MILP, achieving a 50% reduction in optimization time and 37% cost savings in their study A MILP Approach for Multi-Cloud Capacity Allocation [58]. SBSE surveys document widespread use of MOEAs in software engineering Search-Based Software Engineering Survey [59].
- CSP. Architecture as constraint satisfaction is argued and structured into objective, boundary, and trade-off layers in practice-focused writing Architecture as Constraint Satisfaction [16]. Ontology+CSP integration maps domain hierarchies and compatibility rules into solvable models with arc-consistency Integration of Ontologies and CSP [63]. Constraint solvers have been surveyed for software configuration Constraint Solvers for Software Configuration [43]. Industrial feature-model studies evaluate SAT scalability on 130 models across 15 systems Industrial Feature-Model SAT Evaluation [41].
- Hybrid. MaxSAT-based product (re-)configuration computes minimal change sets ReMax Product Re-Configurator [26]. Weighted partial MaxSAT advances core-guided performance CASHWMaxSAT, IJCAI 2025 [6]. Z3 Optimize unifies SMT and multi-objective capabilities Introduction | Online Z3 Guide [40].

Honest gaps. We found no paper that directly optimizes folder hierarchies, naming schemes, and persistence routing as a single problem. Ontology alignment and configuration are closest analogs; library classification remains primarily manual and policy-driven.

## Trade-Off Comparison Table

| Family | Hard-Constraint Enforcement | Multi-Objective Handling | Interpretability | Incremental Tuning | Solver Maturity (5-200 primitives) | Expected Wall-Clock | Human Learning Curve | Agent Learning Curve |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Continuous Optimization | Poor to Fair - hard constraints via penalties/repairs; MIP exact but modeling is brittle | Excellent - native Pareto fronts (NSGA-II), scalarizations | Fair - Pareto plots, metric attributions; no proof traces | Fair - retune weights, re-solve; RL retraining costly | Good - mature MOEAs and MILP solvers NSGA-II Survey [15] HiGHS [61] | Seconds to hours depending on encoding; MIP scales with integrality | Moderate - understanding Pareto and penalties | Moderate - fitness APIs straightforward |
| Constraint Satisfaction | Excellent - first-class hard constraints, unsat cores Z3 - Microsoft Research [19] | Fair - requires MaxSMT or external scalarization | Good to Excellent - unsat cores, named constraints | Excellent - add conjuncts; multi-shot solving | Excellent - Z3/MiniZinc used widely MiniZinc Solvers [38] | Sub-second to minutes at this scale | Moderate - constraint modeling mindset | Excellent - Z3Py, MiniZinc APIs |
| Hybrid COP/MaxSAT | Excellent - hard via assert; soft via assert-soft | Good to Excellent - lexicographic/Pareto/box in Z3 Optimize Z3 Guide [40] | Excellent - must vs prefer separation; objective contributions | Excellent - adjust weights, promote soft to hard | Excellent - Optimize plus CP/MIP backends MiniZinc Solvers [38] | Seconds to minutes; MaxSAT engines efficient CASHWMaxSAT [6] | Moderate - learn hard/soft idioms | Excellent - structured Optimize API |

Takeaways. A* needs uncompromising hard-constraint enforcement and interpretable trade-offs. Hybrid COP/MaxSAT gives both in one workflow. Continuous methods remain useful for exploratory Pareto insight and numeric subproblems but should not anchor v0.

## Neuro-Symbolic and Learning-Guided Constraint Optimization (2020-Present)

Observation. Neuro-symbolic systems augment symbolic solvers with learned guidance or replace parts of the reasoning with differentiable surrogates. NeuroSAT learns a SAT procedure from single-bit supervision, establishing the feasibility of learned search in satisfiability Learning a SAT Solver from Single-Bit Supervision [24]. FastSMT learns solver strategies tailored to datasets of formulas and reports up to 100x speedups relative to a Z3 baseline FastSMT [25]. A systematic review catalogs neuro-symbolic approaches and emphasizes representation, learning, reasoning, and decision-making trends Neuro-symbolic AI: A Survey [21] Neuro-Symbolic AI in 2024: A Systematic Review [53]. Defresne et al. present a differentiable architecture that learns both constraints and objectives via a probabilistic loss, pushing the combinatorial solver out of the training loop for scalability, yet using exact inference at test time on tasks like Sudoku and Min-Cut/Max-Cut Efficient Neuro-Symbolic Learning of Constraints & Objective [3]. Recent work also investigates integrating neural predictors into CDCL SAT solvers to assist branching on both SAT and UNSAT instances Enhancing Modern SAT Solver With Machine Learning Method [4].

Applicability to A*. For domain sizes of 5-200 primitives, classical SMT/MaxSMT will typically be fast enough. However, FastSMT-like strategy learning is attractive for v1 if latency SLOs are missed. Neuro-symbolic learning of constraints/objectives can bootstrap soft-cost shaping from historical operator choices, while keeping Z3 as the enforcement backstop. Embedding a solver in training loops is costly; prefer learning guidance offline and applying it as solver policies at inference time.

Risks. Learned heuristics can misgeneralize; always gate with hard SMT assertions. Keep a fallback to canonical Optimize strategies and track per-instance performance to avoid regressions.

## v0 Recommendation and v1 Evolution Path

v0 functional form (recommended). Hybrid COP/MaxSMT in Z3 Optimize.
- Decision variables: discrete architectural primitives for folder hierarchy, naming templates, archival policies, and store-routing choices.
- Hard constraints: integrity assertions for single source of truth, archival reversibility, and folder-level ontology coherence.
- Soft objectives: 9D cost vector as weighted assert-soft objectives. Start with lexicographic priority reflecting business-criticality; optionally sweep Pareto modes for operator choice Z3 Guide [40].
- Correlated costs: because the effective rank is 4-5, aggregate redundant metrics or tie-break lexicographically to reduce dominance cycling.
- Explanations: enable unsat core extraction and tag each soft assertion with human-readable :id for rationale. Summarize per-solution contributions to each cost term.
- Numeric subproblems: when needed, call an ILP sidecar (e.g., HiGHS/Gurobi) for capacity or cost routing within the same pipeline HiGHS [61] A MILP Approach [58].

Operator workflow. Present 3-7 Pareto-representative solutions with per-constraint satisfaction and per-objective deltas. Allow pinning of substructures and re-solve under these decisions, mirroring interactive MOEA practices but with hard guarantees Interactive MOEA Software Architectures [12].

v1 evolution. Introduce learning-guided strategies and richer soft-cost learning.
- FastSMT-style policy learning across A* instances to reduce wall-clock FastSMT [25].
- Preference learning to tune assert-soft weights from operator selections; keep a safety floor of lexicographic priorities.
- Multi-shot, streaming constraints via clingo multi-shot or Z3 incremental contexts for continuous lifecycles A Tutorial on Hybrid Answer Set Solving with clingo [46].

Redesign triggers. Move to a redesigned v1 when any of the following are true: (1) p95 solve time exceeds SLOs despite strategy learning, (2) operators report inadequate explanations or inability to modify solutions locally, (3) constraint churn forces frequent re-modeling that would be simplified by a different formalism, (4) the problem scale moves beyond a few hundred primitives, suggesting decomposition or specialized encodings.

## Formal Equivalence: A* and S(M,T)

Define S(M,T) = Product_j gate_j(M,T) * Sum_i w_i * phi_i(M,T) * exp(-beta * H_i).

- Gates as hard constraints. If any gate_j = 0, the configuration is invalid. In A*, this is assert gate_j, i.e., a hard SMT clause. This removes all infeasible M from the search space.
- Soft objective. Sum_i w_i * phi_i(M,T) corresponds to weighted assert-soft objectives in MaxSMT. Z3 Optimize minimizes or maximizes weighted sums or uses lexicographic priorities over multiple objectives Introduction | Online Z3 Guide [40].
- Complexity penalty. The factor exp(-beta * H_i) is a monotone transformation of adding beta * H_i as a soft penalty in the objective (since log is monotone): maximizing S is equivalent to minimizing -log S = -Sum_i log(w_i * phi_i) + beta * H_i over feasible M. In practice, one avoids logs by directly adding a soft penalty on H_i with weight beta.

Conclusion. S(M,T) is a special case of Hybrid COP/MaxSMT A* where gates are encoded as hard constraints and the scalarized objective combines weighted performance terms with a complexity penalty. If S is kept multiplicative for interpretability, an equivalent additive objective exists under a monotone transform, preserving argmax/argmin equivalence within the feasible set.

## Synthesis: Cross-Cutting Insights and Decision Framework

- Mechanism. Continuous methods explore trade-offs but require surrogate feasibility; CSP/SMT enforces feasibility with explanations; Hybrid COP/MaxSAT composes both. This triad indicates a natural division of labor: use CSP for validity, Optimize for preferences, MOEA/ILP adjuncts for exploration or numeric subproblems.
- Scope and trade-offs. Continuous covers broad, fuzzy trade spaces; CSP is precise but needs scalarization; Hybrid balances both with moderate modeling complexity. Evidence from architecture MOEAs and deployment MILPs shows gains on quantitative subproblems, while ontology+CSP confirms symbolic structural rules benefit from constraint propagation.
- Time horizon. v0 must earn trust via guarantees and explanations; v1 can add learned guidance to reduce latency. Learning-guided solvers are promising but remain adjuncts; they do not replace the enforcement layer.

Recommendation. Adopt Hybrid COP/MaxSMT for v0; reserve continuous exploration for optional operator-facing what-ifs; plan a v1 that learns solver strategies and preference weights without weakening hard guarantees.

## Unanswered Questions for AgencyA v0 Testbed

- Objective shaping. Which subset of the 9D costs truly drives operator acceptance? Empirically estimate effective rank and set lexicographic tiers.
- Weights and priorities. What weight schedules produce stable, interpretable outcomes across intents and lifecycle stages?
- Explanation UX. Which explanation artifacts (unsat cores, binding constraints, marginal cost deltas) best support operator edits?
- Incremental edit patterns. How often do operators pin substructures and re-solve? Measure re-solve latencies under multi-shot optimization.
- Constraint coverage. Do the initial hard constraints fully capture reversibility and ontology coherence, or are additional invariants needed?
- Store-routing submodel. Does an ILP sidecar outperform pure SMT arithmetic on persistence routing for our data volumes?
- Generalization across T. Do T_human vs. T_agent_external require different soft-cost priors to achieve acceptance?

## References

1. *Towards Effective Deep Learning for Constraint Satisfaction ...*. https://link.springer.com/content/pdf/10.1007/978-3-319-98334-9_38.pdf
2. *Guiding High-Performance SAT Solvers with Unsat-Core ...*. http://arxiv.org/abs/1903.04671
3. *Efficient Neuro-Symbolic Learning of Constraints & Objective*. https://arxiv.org/html/2508.20978v1
4. *Enhancing Modern SAT Solver With Machine Learning Method*. https://dl.acm.org/doi/10.1145/3716368.3735251
5. *Towards Effective Deep Learning forConstraint Satisfaction ...*. https://idm-lab.org/bib/abstracts/papers/cp18.pdf
6. *An Efficient Core-Guided Solver for Weighted Partial MaxSAT*. https://www.ijcai.org/proceedings/2025/0295.pdf
7. *Design Space Exploration - Stanford University*. http://ppl.stanford.edu/papers/mascots19_dse_slides.pdf
8. *Lesson 8: Constraint Optimization Problems (COP)*. https://kindatechnical.com/constraint-programming/lesson-8-constraint-optimization-problems-cop.html
9. *An efficient core-guided solver for weighted partial MaxSAT*. https://dl.acm.org/doi/10.24963/ijcai.2025/295
10. *Design-Space Exploration - an overview | ScienceDirect Topics*. https://www.sciencedirect.com/topics/computer-science/design-space-exploration
11. *Optimize Anything with LLMs - GEPA*. http://gepa-ai.github.io/gepa
12. *Interactive Multi-Objective Evolutionary Optimization of ...*. https://arxiv.org/pdf/2401.04192
13. *Multi-Objective Optimization Accelerates the De Novo Design ...*. http://pmc.ncbi.nlm.nih.gov/articles/PMC11728188
14. *The 10 Most Effective Folder Structure Optimization ...*. https://www.glarysoft.com/how-to/the-10-most-effective-folder-structure-optimization-strategies-for-windows-systems-2/
15. *A comprehensive survey on NSGA-II for multi-objective ...*. https://link.springer.com/article/10.1007/s10462-023-10526-z
16. *Architecture design: a constraint-satisfaction approach ...*. https://avchauzov.github.io/blog/2025/architecture-design-constraint-satisfaction/
17. *(PDF) Ontologies in Knowledge Organization - ResearchGate*. https://www.researchgate.net/publication/345726845_Ontologies_in_Knowledge_Organization
18. *Core SMT Solver Architecture | Z3Prover/z3 | DeepWiki*. https://deepwiki.com/Z3Prover/z3/2-core-smt-solver-architecture
19. *Z3 - Microsoft Research*. http://microsoft.com/en-us/research/project/z3-3
20. *Research on the construction and application of retrieval ...*. http://nature.com/articles/s41598-025-21222-z
21. *Neuro-symbolic artificial intelligence: a survey - Springer*. https://link.springer.com/article/10.1007/s00521-024-09960-z
22. *GitHub - dselsam/neurosat: NeuroSAT: Learning a SAT Solver ...*. https://github.com/dselsam/neurosat
23. *eth-sri/fastsmt: Learning to Solve SMT Formulas Fast - GitHub*. http://github.com/eth-sri/fastsmt
24. *Learning a SAT Solver from Single-Bit Supervision*. http://arxiv.org/abs/1802.03685
25. *FastSMT: Learning to Speed-up SMT Solvers*. https://fastsmt.ethz.ch/
26. *ReMax – A MaxSAT aided Product (Re-)Configurator*. https://www.academia.edu/57294570/ReMax_A_MaxSAT_aided_Product_Re_Configurator
27. *HiGHS optimization solver*. http://en.wikipedia.org/wiki/HiGHS_optimization_solver
28. *Extending Dynamic Backtracking to Solve Weighted Conditional CSPs*. https://cdn.aaai.org/AAAI/2006/AAAI06-005.pdf
29. *A Mixed-Integer Linear Programming Approach to Deploying Base ...*. https://ieeexplore.ieee.org/document/10285116
30. *(PDF) ReMax - A MaxSAT aided product (re-)configurator*. https://www.researchgate.net/publication/265601520_ReMax_-_A_MaxSAT_aided_product_re-configurator
31. *ILASP*. http://ilasp.com/
32. *Classification and Cataloging – Introduction to Library and ...*. https://csi.pressbooks.pub/lis/chapter/classification/
33. *How to Organize a Knowledge Base: A Step-by-Step Guide*. https://bloomfire.com/blog/how-to-organize-a-knowledge-base/
34. *Semantic Constraints Satisfaction Based Improved Quality of ...*. http://beei.org/index.php/EEI/article/download/202/106
35. *North American Industry Classification System (NAICS) U.S. ...*. http://census.gov/naics?chart=2017&details=541512&input=541512
36. *A Physics-Based Constraint Solver for the Site Layout ...*. https://link.springer.com/chapter/10.1007/978-3-031-37189-9_39
37. *OR-Tools vs. Hexaly*. http://hexaly.com/or-tools
38. *3.5. Solving Technologies and Solver Backends — The MiniZinc ...*. https://docs.minizinc.dev/en/stable/solvers.html
39. *Z3 Theorem Prover Benchmark - OpenBenchmarking.org*. https://openbenchmarking.org/test/pts/z3
40. *Introduction | Online Z3 Guide - GitHub Pages*. https://microsoft.github.io/z3guide/docs/optimization/intro/
41. *Evaluating state-of-the-art # SAT solvers on industrial ...*. https://link.springer.com/article/10.1007/s10664-022-10265-9
42. *Timefold configuration | Timefold Solver 0.8.42*. http://docs.timefold.ai/timefold-solver/0.8.x/configuration/configuration
43. *Using Constraint Solvers to Find Valid Software Configurations*. https://www.complang.tuwien.ac.at/raab/constraint_solvers.pdf
44. *Your rules. Our AI. The best decision. - Potassco Solutions*. http://potassco.com/
45. *Answer Set Programming and Knowledge Representation*. https://link.springer.com/subjects/answer-set-programming-and-knowledge-representation
46. *A Tutorial on Hybrid Answer Set Solving with clingo*. https://www.cs.uni-potsdam.de/~torsten/hybris.pdf
47. *Answer Set Programming and Knowledge Representation*. https://www.nature.com/nature-index/topics/l4/answer-set-programming-and-knowledge-representation
48. *Programming with CLINGO*. https://www.cs.utexas.edu/~vl/teaching/378/firmf.pdf
49. *Satisfiability modulo theories - Wikipedia*. http://en.wikipedia.org/wiki/Satisfiability_modulo_theories
50. *Objective functions in Z3 - Hey There Buddo!*. https://www.philipzucker.com/z3-rise4fun/optimization.html
51. *Z3.Optimize - GitHub Pages*. https://z3prover.github.io/api/html/ml/Z3.Optimize.html
52. *Arithmetical Optimization | Online Z3 Guide - GitHub Pages*. https://microsoft.github.io/z3guide/docs/optimization/arithmeticaloptimization/
53. [[2501.05435] Neuro-Symbolic AI in 2024: A Systematic Review](https://arxiv.org/abs/2501.05435)
54. [[1506.08905] Understanding VSIDS Branching Heuristics in ...](https://ar5iv.labs.arxiv.org/html/1506.08905)
55. *About – Prof. Chandra Nair*. http://chandra.ie.cuhk.edu.hk/bio.html
56. [arXiv:2303.01141v3 [cs.LG] 14 Dec 2023](https://arxiv.org/pdf/2303.01141v3)
57. *Neuro-symbolic agentic AI: Architectures, integration ...*. https://www.sciencedirect.com/science/article/pii/S1574013726000110
58. *A mixed integer linear programming optimization approach for ...*. https://www.sciencedirect.com/science/article/pii/S0164121216301996
59. *Search-based software engineering: Trends, techniques and ...*. https://dl.acm.org/doi/10.1145/2379776.2379787
60. *SRG: Score-based Relaxation-guided Generation for Mixed ...*. https://arxiv.org/pdf/2603.24033v2
61. *HiGHS - High-performance parallel linear optimization software*. http://highs.dev/
62. *Semantic similarity and machine learning with ontologies - PMC*. http://pmc.ncbi.nlm.nih.gov/articles/PMC8293838
63. *Integration of Ontologies and Constraint Satisfaction ...*. https://imt-mines-albi.hal.science/hal-03536894/document
64. *Learning to Match Ontologies on the Semantic Web*. https://pages.cs.wisc.edu/~anhai/papers/glue-vldbj.pdf
65. *Our Products and Solutions - JANZZ.technology*. http://janzz.technology/our-products-and-solutions
66. *Integration of Ontologies and Constraint Satisfaction ...*. https://ieeexplore.ieee.org/document/9672918
