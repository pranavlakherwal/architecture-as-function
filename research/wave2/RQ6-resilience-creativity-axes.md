# Cost Vector Decisions For Resilient Creative Architectures

## Executive Summary

- **Resilience Is A Scenario Envelope**: Hollnagel's Resilience Assessment Grid evaluates **4 potentials** - respond, monitor, learn, and anticipate - while Google SRE operationalizes reliability through SLIs, SLOs, and error budgets Resilience Assessment Grid [21], Google SRE: Service Level Objectives [65], Google SRE: Error Budget Policy [18] -> do not add generic `c_resilience`; model resilience as scenario-indexed hard constraints plus a small number of risk functionals.
- **Blast Radius Is The Missing Resilience Scalar**: Chaos engineering defines resilience work as experiments against measurable steady state behavior and recommends minimizing blast radius Principles of Chaos Engineering [64], Chaos Engineering [23] -> if current axes cannot capture failure containment, add optional `c_blast = E[impact | single failure event]`, not a broad resilience axis.
- **Resilience Should Bound `c_drift`, `c_loss`, And `c_reverse`**: Woods' graceful extensibility work treats brittleness as collapse when adaptive capacity saturates, and Taleb distinguishes the resilient system that stays the same from the antifragile system that benefits from shocks The Theory of Graceful Extensibility [20], Antifragile [59] -> encode resilience as bounds on drift, loss, recovery, and blast-radius scenarios, with intent-level risk posture in `I`.
- **Creativity Is Intent Plus Output Quality**: Design creativity research commonly measures creativity through **novelty plus usefulness**, while Alexander defines design quality as fitness between form and context Assessing Design Creativity [31], Assessment of Creative Potential via Novelty and Usefulness [13], Notes on the Synthesis of Form [12] -> place creativity in `I` as a novelty/search appetite and score generated architectures with `q_creativity`, not as a cost in `C`.
- **Onboarding Is A Split Variable**: SPACE measures productivity across **5 dimensions** - satisfaction, performance, activity, communication and collaboration, and efficiency and flow - and DevEx identifies **3 dimensions** - feedback loops, cognitive load, and flow state The SPACE of Developer Productivity [33], DevEx: What Actually Drives Productivity [36] -> remove observed `c_onboard_total` from intrinsic `C`; retain only an architecture-intrinsic learnability residual, and move team/tooling capacity to `T`.
- **Reverse Cost Is Also Split**: DORA-style failed-deployment recovery time measures a team's ability to detect, troubleshoot, and restore service, while Git, database transactions, Statsig, and LaunchDarkly show undo cost is strongly shaped by tooling DORA Failed Deployment Recovery Time [40], Git: Undoing Things [8], PostgreSQL ROLLBACK, Statsig Feature Flags [25], LaunchDarkly [10] -> split `c_reverse` into architecture irreversibility and `T_reverse_capability`; do not keep total rollback time as a pure architecture axis.
- **Dimensionality Should Fall From 9 To 7**: If `c_onboard_total` and `c_reverse_total` are moved out of `C`, core `C` falls from **9 axes to 7 axes**; because both removed axes are composites of existing architecture costs plus team/tooling variables, effective rank likely drops from **4-5 to 3-4** -> adopt a smaller intrinsic `C` and a richer `T`, while keeping scenario diagnostics for resilience and reversibility.

## Decision Register: Four Placement Calls

| Construct | Literature Signal | Recommended Placement | Why This Is Defensible |
|---|---|---|---|
| Resilience | Hollnagel uses a **4-potential** profile; SRE uses SLOs, SLIs, error budgets; chaos engineering uses steady-state experiments and blast-radius control | Something else: a scenario-indexed constraint and risk envelope; optional `c_blast` | Resilience is not one monotonic cost. It is adaptive behavior under disturbances, so it belongs in constraints over scenarios and in `I` as risk posture |
| Creativity | Design research measures novelty plus usefulness; Alexander measures fit between form and context; ATAM evaluates quality-attribute scenarios and tradeoffs | Intent parameter plus output-side quality score | Creativity is a goal for generation and a property of the generated architecture, not a cost to minimize |
| `c_onboard` | SPACE and DevEx show productivity/onboarding are multidimensional and tool/team/process dependent; Google research points to code quality as an intrinsic contributor | Split, but remove observed onboarding time from core `C` | Total onboarding time is confounded. Keep architecture learnability as a residual or submetric; put onboarding capability in `T` |
| `c_reverse` | DORA recovery metrics, Git undo, database rollback, and feature flags show rollback depends on release/tooling capabilities; architecture still matters for state, coupling, and side effects | Split, but remove observed rollback time from core `C` | Total undo time is a team/tooling outcome. Keep architecture irreversibility as a scenario risk; put rollback capability in `T` |

The common pattern is that `C` should measure architecture-intrinsic burdens, while `I` specifies goals and `T` specifies the team's ability to realize or mitigate those burdens. The mistake to avoid is putting downstream operational outcomes directly into `C` when they are produced by architecture, tooling, team skill, and process jointly.

## Part A1: Resilience Belongs In A Scenario Risk Envelope

Hollnagel's Safety-II and resilience engineering view resilience as the ability to sustain required operations under expected and unexpected conditions by adjusting functioning before, during, or after events. His Resilience Assessment Grid does not reduce resilience to one scalar. It evaluates **4 basic potentials**: the ability to respond, monitor, learn, and anticipate, using question sets and Likert-style ratings to form a resilience profile Resilience Assessment Grid [21]. That matters for `A*(I, L, K, T)` because a profile is closer to a constraint system than to a single additive cost.

Woods and Cook push the same conclusion from a complex-systems direction. Cook's "How Complex Systems Fail" argues that complex systems are defended by layers, contain latent failures, and depend on practitioner adaptation at the sharp end How Complex Systems Fail [54]. Woods' graceful extensibility work defines resilience in terms of adaptive capacity at the boundary of the system's modeled operating envelope. Brittleness appears when adaptive capacity saturates and the system collapses rather than extending gracefully The Theory of Graceful Extensibility [20]. This is a nonlinear boundary property, not a linear marginal cost.

Taleb's antifragility gives an important caution: robustness, resilience, and antifragility are not interchangeable. Taleb distinguishes systems that are fragile under volatility, systems that are robust or resilient and stay the same, and systems that are antifragile and benefit from volatility Antifragile [59]. If `I` says "resilient," `A*` must know whether the user means shock absorption, rebound, graceful extensibility, or antifragile learning. That is an intent-level posture, not just a cost weight.

The SRE and chaos engineering literatures show how to operationalize this in software. Google SRE defines an SLI as a quantitative service-level measure, an SLO as a target value or range for that measure, and an error budget as the tolerable unreliability left by the SLO Google SRE: Service Level Objectives [65], Google SRE: Error Budget Policy [18]. Chaos engineering defines the discipline as experimenting on a system to build confidence that it withstands turbulent production conditions; experiments start from measurable steady-state behavior and should minimize blast radius Principles of Chaos Engineering [64], Chaos Engineering [23].

**Recommendation for resilience:** do not create a generic `c_resilience` axis. Represent resilience as:

```text
I_resilience = {
  posture: robust | rebound | graceful_extensibility | antifragile,
  SLOs and error budgets,
  scenario suite S_R,
  risk appetite alpha,
  required recovery and containment bounds
}

R(A, T, s) = {
  c_loss(A, s) <= lambda_s,
  c_drift(A, s) <= delta_s,
  c_reverse_arch(A, s) <= rho_s,
  MTTR(A, T, s) <= tau_s,
  c_blast(A, s) <= beta_s
}
```

Use hard constraints when the user specifies unacceptable outcomes, such as "no more than X data loss" or "restore within Y minutes." Use weighted objectives only for tradeable goals. Add optional `c_blast` when failure containment is not already represented by `c_loss`, `c_drift`, and `c_reverse_arch`.

### Should Resilience Map To Bounds Or To `c_blast`?

The answer is both, with different status.

| Resilience Concern | Best Mathematical Form | Reason |
|---|---|---|
| Data loss under failure | Bound on `c_loss` | SRE and DORA-style recovery metrics treat restoration and loss as operational outcomes to keep within targets |
| Semantic or model drift after disturbance | Bound on `c_drift` | Resilience includes preserving required operations under perturbation, so unacceptable drift should be constrained |
| Ability to undo architectural harm | Bound on architecture-intrinsic `c_reverse_arch` | Recovery is part architecture and part team/tooling; constrain the intrinsic part and condition on `T` for total recovery |
| Failure containment | Optional `c_blast` | Chaos engineering explicitly emphasizes blast-radius minimization; a single failure's scope may vary independently of data loss or rollback speed |
| Adaptive capacity | Scenario suite plus slack variables | Hollnagel and Woods treat resilience as profile and capacity, not as a simple cost |

So `c_blast` is justified only when a single failure event's expected impact is a separable architectural property. Examples include tenant isolation, cell-based architecture, circuit breakers, bulkheads, and bounded queues. If a monolith and a cell-based architecture have the same expected data loss and rollback time but one affects **100 percent** of tenants while the other affects **1 cell**, `c_blast` captures a real architectural difference.

## Part A2: Creativity Is Intent Plus Output Quality

Creativity is different from resilience because it is primarily about generation and evaluation, not survival under disturbance. Nigel Cross's design research treats design thinking as a distinct way of knowing in which designers frame problems and solutions together rather than merely solve a fixed problem Designerly Ways of Knowing and Thinking [80], Design Thinking [79]. That maps directly to `A*`: the generator needs a parameter telling it how much to explore, reframe, and recombine, not a cost axis to minimize.

Alexander gives the architecture-specific quality test. In *Notes on the Synthesis of Form*, he says every design problem begins with an effort to achieve fitness between the form and its context; the form is the solution and the context defines the problem Notes on the Synthesis of Form [12]. His pattern-language work then treats patterns as reusable design relationships that can be combined and adapted to solve recurring problems Christopher Alexander: The Father of Pattern Language [11]. The implication is that creative architecture is not random novelty. It is novel fit.

Empirical design-creativity research makes this measurable. Shah, Smith, and Vargas-Hernandez propose assessing design creativity as a function of novelty and usefulness Assessing Design Creativity [31]. A later design-science paper similarly frames creative potential through novelty and usefulness and reports statistical support for both dimensions Assessment of Creative Potential via Novelty and Usefulness [13]. The Creative Product Semantic Scale tradition also treats creative products as assessable across multiple dimensions, not as mere originality Creative Product Semantic Scale [71].

Software architecture quality literature adds a guardrail. The Architecture Tradeoff Analysis Method, associated with Bass, Clements, Kazman, Klein, and SEI, evaluates architecture against quality-attribute scenarios, utility trees, risks, non-risks, sensitivity points, and tradeoffs ATAM: Method for Architecture Evaluation [14], Architecture Tradeoff Analysis Method - ATAM [82]. That means a creative architecture is not good merely because it is unusual; it must still satisfy performance, modifiability, security, availability, and other quality scenarios.

**Recommendation for creativity:** place creativity primarily in `I`, and evaluate it on the output.

```text
I_creativity = {
  novelty_target: low | medium | high | percentile target,
  exploration_budget,
  allowed_pattern_distance_from_K,
  analogy_domains,
  must_satisfy_quality_scenarios,
  unacceptable novelty risks
}

q_creativity(A | I, K) =
  w_n * novelty(A, K)
  + w_u * usefulness(A, I)
  + w_v * stakeholder_value(A, I)
  + w_f * fit(A, context)
  - w_r * quality_scenario_violations(A)
```

Do not add `c_creativity` to `C`. A cost vector conventionally contains burdens to minimize. Creativity is either a desired output quality or an exploration policy. If creativity creates downstream costs, those costs should appear through existing axes, such as higher cognitive burden, higher drift risk, weaker reversibility, or lower fit to quality scenarios.

## Part B1: `c_onboard` Should Be Split, Then Removed As A Total Cost Axis

The strongest evidence against treating observed onboarding time as an intrinsic architecture axis is the developer productivity literature. The SPACE framework explicitly warns against one-dimensional productivity measurement. It defines productivity across **5 dimensions**: satisfaction and well-being, performance, activity, communication and collaboration, and efficiency and flow The SPACE of Developer Productivity [33], Microsoft Research: The SPACE of Developer Productivity [37]. Onboarding cuts across all five: a new engineer needs usable tools, social access, feedback, review loops, and confidence, not just a clean architecture.

The DevEx framework is even more direct. It identifies **3 dimensions** that drive developer productivity: feedback loops, cognitive load, and flow state DevEx: What Actually Drives Productivity [36]. Architecture affects cognitive load, but tooling and process affect all three. Slow builds, missing docs, unclear ownership, unavailable mentors, and long review cycles can make a good architecture hard to onboard into. Conversely, excellent code search, generated local environments, walkthroughs, and mentoring can make a complex architecture navigable.

Google's FSE 2022 paper on developer productivity at Google focuses on code quality as a driver of productivity, which supports keeping an architecture-intrinsic component What Improves Developer Productivity at Google? Code Quality [99]. But onboarding studies show why the total metric is still confounded. A case study of onboarding in software teams asks how tasks influence a new developer's onboarding experience, indicating that assigned work and team strategy shape ramp-up A Case Study of Onboarding in Software Teams [96]. A 2025 systematic literature review focuses on software solutions, tools, applications, and platforms designed to facilitate newcomer onboarding, which is direct evidence that onboarding is tool-mediated Software Solutions for Newcomers' Onboarding in Software Projects [87]. Atlassian's DevEx material similarly frames developer experience as the interaction between developers and the tools, processes, and environments they use Atlassian: What Is Developer Experience [91].

**Call on `c_onboard`: choose (c), split.** Do not keep observed `c_onboard_total` as a core axis in `C`. Instead:

```text
c_onboard_total(repo, team, tooling) =
  c_learn_arch(A) + T_onboard_friction(T) + person_fit + task_selection + noise
```

- Keep `c_learn_arch(A)` only if you need an architecture-intrinsic learnability or cognitive-load residual.
- Prefer folding `c_learn_arch` into an existing intrinsic maintainability, complexity, or comprehensibility axis rather than preserving `c_onboard` as a separate axis.
- Move `T_onboard_friction` into `T`, with fields for documentation quality, environment setup automation, code search, build/test latency, mentoring capacity, review latency, ownership clarity, and prior skill distribution.

This is compatible with Wave 1's SPACE-based recommendation. SPACE does not prove architecture is irrelevant; it proves the observed onboarding outcome is a multi-factor productivity variable. Therefore, total onboarding time belongs in `T` or in evaluation data conditioned on `T`, not in architecture-intrinsic `C`.

## Part B2: `c_reverse` Should Be Split Into Architecture Irreversibility And Tooling Capability

Rollback and undo are also composite variables. DORA-style failed-deployment recovery time is explicitly a delivery and operations metric: shorter recovery time indicates a team's ability to detect issues, troubleshoot them, and restore the system while minimizing downtime DORA Failed Deployment Recovery Time [40]. That is not pure architecture. It includes monitoring, alerting, deployment automation, runbooks, team skill, and release policy. DORA itself describes its research program as studying capabilities that drive software delivery and operations performance DORA Research [38].

Version control and databases show the tooling side. Git's official "Undoing Things" chapter warns that undo operations are not always reversible and that users may lose work if they do them wrong Git: Undoing Things [8]. PostgreSQL defines `ROLLBACK` as discarding all updates made by the current transaction PostgreSQL ROLLBACK, while SQL Server's `ROLLBACK TRANSACTION` can roll back to the beginning of a transaction or to a savepoint SQL Server ROLLBACK TRANSACTION. These capabilities are powerful, but they depend on whether the change is inside a transaction, whether irreversible side effects occurred, and whether the architecture isolates state.

Feature flags show the release-platform side. Statsig states that feature flags let teams toggle product behavior in real time without deploying new code Statsig Feature Flags [25]. LaunchDarkly describes feature flags, progressive delivery, automated rollback, and runtime control LaunchDarkly [10], and its kill-switch material explicitly frames flags as a way to roll back buggy features quickly LaunchDarkly Kill Switch [47]. These are not architecture-intrinsic properties alone; they are team and platform capabilities.

Architecture still matters. A stateless UI feature behind a flag can often be reversed by toggling the flag. A schema migration that destroys data, emits external side effects, changes public API contracts, or tightly couples services may be difficult or impossible to reverse even with excellent tooling. That is the intrinsic component.

**Call on `c_reverse`: choose (c), split.** Remove observed `c_reverse_total` from core `C`, but keep architecture-intrinsic reversibility in the resilience scenario model.

```text
c_reverse_total(change, A, T) =
  c_irreversibility_arch(change, A)
  + T_reverse_friction(T)
  + incident_detection_time
  + operator_execution_time
  + noise
```

Use `c_irreversibility_arch` as a scenario-level diagnostic or constraint, not necessarily a standalone axis. It should capture state coupling, destructive migrations, external side effects, backward-compatibility breaks, dependency propagation, and blast radius. Put `T_reverse_friction` in `T`, with fields for CI/CD maturity, version-control practice, feature-flag coverage, database rollback and migration tooling, backup/restore capability, observability, runbooks, and SRE/on-call maturity.

## Measurement Controls If `c_onboard` Or `c_reverse` Remain In `C`

If you decide to keep either construct in `C`, the measurement protocol must isolate the architecture-intrinsic residual from team and tooling confounders. Otherwise, `C` will learn that one architecture is better simply because one team had better docs, faster CI, or stronger mentors.

| Construct | Confounder | Control Protocol | Metric To Record |
|---|---|---|---|
| `c_onboard` | Newcomer prior skill | Match participants by experience, language familiarity, and domain familiarity | Background-adjusted time to first correct task |
| `c_onboard` | Documentation and mentoring | Freeze docs, standardize mentor access, or measure docs and mentoring as `T` covariates | Time to environment setup, time to first merged PR, help requests |
| `c_onboard` | Tooling latency | Use the same IDE, code search, local setup, build, and test environment across repos | Build/test wait time, setup failures, feedback-loop latency |
| `c_onboard` | Task selection | Use equivalent onboarding tasks with predefined acceptance tests | Completion time, defect rate, review iterations |
| `c_onboard` | Team process | Hold review policy, branch policy, and communication channels constant | Review latency, number of blocked intervals |
| `c_reverse` | CI/CD maturity | Run rollback tests under the same deployment pipeline or model pipeline quality in `T` | Time to rollback command, pipeline failure rate |
| `c_reverse` | Feature-flag coverage | Either disable flags for intrinsic measurement or include flag coverage in `T` | Percent of change surface behind reversible flags |
| `c_reverse` | Database tooling | Standardize migration tools, backups, and transaction policy | Data-loss risk, restore time, migration reversibility |
| `c_reverse` | Observability and detection | Separate detection time from execution time | MTTD, MTTR, failed-deployment recovery time |
| `c_reverse` | Operator expertise | Use scripted runbooks and matched operators | Human execution time, rollback error count |

The best statistical approach is a mixed-effects or hierarchical model: architecture/repo as one effect, team/tooling as another, and task/person as controls. For stronger causal evidence, use a difference-in-differences design around an architecture refactor while holding the team and tooling stable. For synthetic benchmarking, run the same tasks on multiple repos under a containerized, standardized toolchain.

## Revised `C`, `I`, `K`, And `T` Schema

The revised schema should separate intrinsic architecture costs, intent-level goals, knowledge taxonomy, and team/tooling capabilities.

```text
A*(I, L, K, T) -> candidate architecture A plus diagnostics D
```

### Core Cost Vector

Let the old vector be:

```text
C_old = (c_1, c_2, c_3, c_4, c_5, c_6, c_7, c_onboard_total, c_reverse_total)
```

The revised core vector is:

```text
C_core = (c_1, c_2, c_3, c_4, c_5, c_6, c_7)
```

where the retained `c_i` are the architecture-intrinsic axes already present in your framework, including at least the known intrinsic axes such as `c_drift` and `c_loss` if those are in the existing taxonomy. Do not include observed onboarding time or observed rollback time as core axes.

Optional diagnostics sit outside the core vector:

```text
D_resilience = {
  c_blast(A, s),
  c_loss(A, s),
  c_drift(A, s),
  c_irreversibility_arch(A, s),
  MTTR(A, T, s),
  error_budget_burn(A, T, s)
}

D_creativity = {
  novelty(A, K),
  usefulness(A, I),
  stakeholder_value(A, I),
  fit(A, context),
  quality_scenario_pass_rate(A)
}
```

If the domain is safety-critical, multi-tenant, regulated, or high-scale, promote `c_blast` into the optimized vector as an optional eighth axis:

```text
C_resilience_critical = C_core + (c_blast)
```

Do this only when blast radius has independent variance from `c_loss`, `c_drift`, and reversibility.

### Intent `I`

`I` should now include explicit goal-shaping parameters:

```text
I = {
  product_goals,
  business_goals,
  quality_attribute_priorities,
  I_resilience,
  I_creativity,
  unacceptable_constraints,
  scenario_suite
}
```

`I_resilience` specifies the desired posture: robust, rebound-oriented, graceful-extensible, or antifragile. It also specifies SLOs, error budgets, recovery bounds, blast-radius bounds, and failure scenarios. `I_creativity` specifies novelty target, exploration budget, analogy domains, pattern-distance allowance from `K`, and required quality-attribute scenarios.

### Knowledge Taxonomy `K`

`K` should distinguish architecture knowledge from evaluation knowledge:

```text
K = {
  architecture_patterns,
  anti_patterns,
  quality_attribute_tactics,
  ATAM_scenario_templates,
  failure_modes,
  rollback_patterns,
  migration_patterns,
  design_exemplar_corpus,
  novelty_baseline_corpus
}
```

This lets `A*` ask whether a generated architecture is novel relative to known patterns, useful relative to the user intent, and safe relative to known failure modes.

### Team And Tooling `T`

`T` should become richer because it now absorbs observed onboarding and rollback capabilities:

```text
T = {
  T_onboard: {
    documentation_quality,
    docs_freshness,
    setup_automation,
    code_search_quality,
    build_test_latency,
    mentor_capacity,
    review_latency,
    ownership_clarity,
    prior_skill_distribution
  },

  T_reverse: {
    version_control_practice,
    CI_CD_maturity,
    feature_flag_coverage,
    database_transaction_and_migration_tooling,
    backup_restore_capability,
    observability,
    runbook_quality,
    incident_response_maturity,
    SRE_maturity
  },

  T_devex: {
    SPACE_dimensions,
    feedback_loop_latency,
    cognitive_load_sources,
    flow_interruptions,
    communication_and_collaboration_practices
  }
}
```

This schema lets `A*` condition recommendations on reality. A team with weak rollback tooling should receive architectures that minimize irreversible changes and require smaller blast radius. A team with mature flags, migrations, and observability can safely consider architectures that rely on progressive delivery and fast rollback.

## Dimensionality And Effective Rank Projection

If `c_onboard_total` and `c_reverse_total` move out of `C`, the nominal dimension drops from **9 to 7**. That part is straightforward.

The effective-rank prediction is also directionally sound. Effective rank depends on how much independent variance each axis contributes. The evidence suggests `c_onboard_total` and `c_reverse_total` are not independent architecture dimensions. `c_onboard_total` loads on architecture/code quality, cognitive load, feedback loops, documentation, mentoring, and setup tooling DevEx: What Actually Drives Productivity [36], What Improves Developer Productivity at Google? Code Quality [99]. `c_reverse_total` loads on architecture irreversibility, data-loss risk, blast radius, observability, CI/CD, feature flags, database tooling, and incident response DORA Failed Deployment Recovery Time [40], Statsig Feature Flags [25], PostgreSQL ROLLBACK.

So a measured 9-axis cost matrix likely contains collinearity: onboarding overlaps with complexity, maintainability, drift, build/test feedback, and team process; reverse overlaps with loss, blast radius, coupling, statefulness, and deployment tooling. Removing the two observed total axes should reduce noise and lower empirical rank from about **4-5 to 3-4**, provided the remaining seven axes are truly architecture-intrinsic. If you add optional `c_blast`, rank may rise only if blast radius varies independently of loss and recovery time.

The K taxonomy should change accordingly. Do not create a separate K class for "onboarding cost" or "reverse cost" as if they were primitive architecture properties. Instead, add K classes for learnability patterns, rollback patterns, migration patterns, failure-domain patterns, and DevEx/SRE capability mappings. These feed scenario evaluation and `T`, rather than inflating `C`.

## Synthesis

| Dimension | Resilience | Creativity | `c_onboard` | `c_reverse` |
|---|---|---|---|---|
| Primary mechanism | Adapt under disturbance | Generate novel fit | Learn a codebase and workflow | Undo or contain change harm |
| Best home | Scenario constraints plus optional `c_blast`; posture in `I` | `I_creativity` plus output score `q_creativity` | Split: intrinsic learnability residual plus `T_onboard` | Split: intrinsic irreversibility plus `T_reverse` |
| Main evidence base | Hollnagel, Woods/Cook, SRE, chaos engineering, Taleb | Cross, Alexander, novelty/usefulness research, ATAM | SPACE, DevEx, Google code-quality research, onboarding studies | DORA recovery, Git undo, DB rollback, feature flags |
| Time horizon | Runtime and incident horizon | Design search and selection horizon | First days to months of contributor ramp-up | Deployment, migration, and incident horizon |
| Risk if modeled as simple cost | Hides nonlinear boundary failure and blast radius | Penalizes desired novelty and collapses exploration | Confounds architecture with docs, mentors, tools, and team process | Confounds architecture with CI/CD, flags, observability, and DB tooling |
| Recommended action | Add resilience envelope `R(A,T,s)` and optional `c_blast` | Add `I_creativity` and `q_creativity` | Remove total axis from `C`; enrich `T` | Remove total axis from `C`; enrich `T` |

The non-obvious tension is that resilience and creativity both matter, but they enter the econometric framing in opposite ways. Resilience is mostly a constraint on unacceptable downside under stress. Creativity is mostly an exploration and selection parameter that increases the chance of discovering high-fit architectures. Treating both as ordinary costs would erase this distinction.

The second tension is that `c_onboard` and `c_reverse` feel architecture-related because architecture clearly affects them. But the literature shows that the observed quantities are capability-mediated outcomes. A well-structured repo with bad docs and slow builds can onboard poorly; a risky migration with excellent feature flags may be operationally reversible until it touches irreversible data. Therefore, the cleanest model is not "architecture versus tooling." It is a split model: architecture-intrinsic burden in `C` or diagnostics, capability in `T`, and scenario outcomes computed from both.

The final design rule is: keep `C` small, intrinsic, and orthogonal; put goals in `I`; put team/tooling capability in `T`; put resilience and creativity in scenario diagnostics and output-quality functions. That gives `A*` better causal semantics and better empirical measurability.

## Final Recommendations

1. **Resilience:** do not add `c_resilience`. Add `I_resilience`, a resilience scenario suite, hard bounds over `c_drift`, `c_loss`, `c_irreversibility_arch`, MTTR, and error-budget burn, plus optional `c_blast` when failure containment is separable.
2. **Creativity:** do not add `c_creativity`. Add `I_creativity` to parameterize search and add `q_creativity(A | I, K)` to score output novelty, usefulness, value, fit, and ATAM-style quality-scenario satisfaction.
3. **`c_onboard`:** choose split. Remove `c_onboard_total` from core `C`; retain only architecture learnability as a residual or fold it into an existing intrinsic complexity/maintainability axis; move onboarding capability to `T_onboard`.
4. **`c_reverse`:** choose split. Remove `c_reverse_total` from core `C`; retain architecture irreversibility as a scenario diagnostic or constraint; move rollback capability to `T_reverse`.
5. **Dimensionality:** adopt `C_core` with **7 intrinsic axes** after removing the two total outcome axes. Expect effective rank to drop from **4-5 to 3-4** unless optional `c_blast` has strong independent variance.

## References

1. *DX - Crunchbase Company Profile & Funding*. https://www.crunchbase.com/organization/dx
2. *The SPACE Framework: A Complete Guide to Developer Productivity*. https://space-framework.com/
3. *Atlassian - GitHub*. https://github.com/atlassian
4. *Digital Onboarding*. http://github.com/digitalonboarding
5. *The SPACE of Developer Productivity.docx*. http://coursehero.com/file/252817886/The-SPACE-of-Developer-Productivitydocx
6. *LaunchDarkly vs Split*. http://flagsmith.com/compare/launchdarkly-vs-split
7. *LaunchDarkly Migration Guide - Statsig Documentation*. https://docs.statsig.com/guides/migrate-from-launchdarkly
8. *Git - Undoing Things*. https://git-scm.com/book/en/v2/Git-Basics-Undoing-Things
9. *DORA metrics | Technology Radar | Thoughtworks Brazil*. http://thoughtworks.com/en-br/radar/techniques/dora-metrics
10. *LaunchDarkly: Runtime Control for AI-Era Software | Feature ...*. http://launchdarkly.com/
11. *Christopher Alexander: The father of pattern language*. http://designsystems.com/christopher-alexander-the-father-of-pattern-language
12. *Notes on the Synthesis of Form - ia601508.us.archive.org*. https://ia601508.us.archive.org/33/items/AlexanderChristopherNotesOnTheSynthesisOfForm/Alexander_Christopher_Notes_on_the_Synthesis_of_Form.pdf
13. *Assessment of the creative potential of design problems via ...*. https://www.cambridge.org/core/journals/design-science/article/assessment-of-the-creative-potential-of-design-problems-via-novelty-and-usefulness/ECBD7B65EA50FEBB0831C6D4A20AC585
14. *ATAM: Method for Architecture Evaluation - SEI Digital Library*. http://sei.cmu.edu/library/atam-method-for-architecture-evaluation
15. *Notes on the Synthesis of Form — Harvard University Press*. https://www.hup.harvard.edu/books/9780674627512
16. *Building and revising adaptive capacity sharing for technical ...*. https://www.sciencedirect.com/science/article/pii/S0003687020301903
17. *HMCTS customer story*. http://dynatrace.com/customers/hmcts
18. *Google SRE - Error Budget Policy for Service Reliability*. https://sre.google/workbook/error-budget-policy/
19. *Safety-II in Practice: Developing the Resilience Potentials*. https://www.erikhollnagel.com/onewebmedia/Blurp.pdf
20. *(PDF) The Theory of Graceful Extensibility: Basic rules that ...*. https://www.researchgate.net/publication/327427067_The_Theory_of_Graceful_Extensibility_Basic_rules_that_govern_adaptive_systems
21. *Resilience Assessment Grid - erikhollnagel.com*. https://erikhollnagel.com/ideas/resilience%20assessment%20grid.html
22. *Must-Know Site Reliability Engineering (SRE) Terminology*. http://cloudsoft.io/blog/site-reliability-engineering-sre-glossary
23. *Chaos Engineering - arXiv.org*. https://arxiv.org/pdf/1702.05843
24. *Continuous Verification - Casey Rosenthal, Verica*. http://ott.techstrong.tv/spotlight-interviews/videos/continuous-verification-casey-rosenthal-verica
25. *Feature Flags - Statsig Documentation*. https://docs.statsig.com/feature-flags/overview
26. *LaunchDarkly: Feature Flagging Platform Explained*. http://growthbook.io/insights/launchdarkly-feature-flagging-platform-explained
27. *Feature Flags | LaunchDarkly | Documentation*. https://launchdarkly.com/docs/api/feature-flags
28. *Cloud DevOps: What the Numbers Can't Hide*. http://ensolvers.com/post/cloud-devops-what-the-numbers-cant-hide
29. *Designerly Ways of Knowing and Thinking | Springer Nature Link*. https://link.springer.com/book/10.1007/978-1-4471-7541-4
30. *SEI ATAM Example | PDF | Software Architecture | Scenario ...*. http://scribd.com/document/596357149/SEI-ATAM-Example
31. *Assessing design creativity*. https://dm.iisc.ac.in/cpdm/ideaslab/publications/UID_45.pdf
32. *Designerly Ways of Knowing and Thinking*. https://oro.open.ac.uk/104099/
33. *The SPACE of Developer Productivity - ACM Queue*. https://queue.acm.org/detail.cfm?id=3454124
34. *Onboarding Developers Faster The Atlassian Based Blueprint*. https://www.atlas-bench.com/blog/onboarding-developers-faster-the-atlassian-based-blueprint
35. [[Hiring] Technical Lead - Developer Experience @Arbor Education](http://remotive.com/remote/jobs/software-development/technical-lead-developer-experience-4511213)
36. *DevEx: What Actually Drives Productivity - ACM Queue*. https://queue.acm.org/detail.cfm?id=3595878
37. *The SPACE of Developer Productivity: There's more to it than ...*. https://www.microsoft.com/en-us/research/publication/the-space-of-developer-productivity-theres-more-to-it-than-you-think/
38. *DORA | Research - Dora.dev*. https://dora.dev/research
39. *Dora.dev*. https://dora.dev/
40. *DORA - Failed Deployment Recovery Time | Apache DevLake ...*. https://devlake.apache.org/docs/Metrics/FailedDeploymentRecoveryTime/
41. *Use Four Keys metrics like change failure rate to measure ...*. https://cloud.google.com/blog/products/devops-sre/using-the-four-keys-to-measure-your-devops-performance
42. *Onboarding - GitHub Docs*. https://docs.github.com/en/get-started/onboarding
43. *Revolutionizing Newcomers’ Onboarding Process in OSS ...*. https://dl.acm.org/doi/10.1145/3715767
44. *Newcomer adjustment: Examining the role of managers ...*. http://psycnet.apa.org/record/2017-10515-001
45. *Swimm: Business Model Canvas – businessmodelcanvastemplate ...*. http://businessmodelcanvastemplate.com/products/swimm-business-model-canvas
46. *Check Feature Gate(s) - Statsig Documentation*. http://docs.statsig.com/api-reference/feature-gates/check-feature-gates
47. *How to instantly roll back buggy features with LaunchDarkly’s ...*. https://launchdarkly.com/blog/how-to-instantly-roll-back-buggy-features-with-launchdarkly-kill-switch/
48. *Guarded rollouts | LaunchDarkly | Documentation*. https://launchdarkly.com/docs/home/releases/guarded-rollouts
49. *ROLLBACK TRANSACTION (Transact-SQL) - SQL Server*. http://learn.microsoft.com/en-us/sql/t-sql/language-elements/rollback-transaction-transact-sql?view=sql-server-ver17
50. *Documentation: 18: ROLLBACK*. http://postgresql.org/docs/current/sql-rollback.html
51. *Transactions - Oracle Help Center*. https://docs.oracle.com/en/database/oracle/oracle-database/19/cncpt/transactions.html
52. *Understanding Atomicity in PostgreSQL: A Deep Dive into the ...*. https://dev.to/kfir-g/understanding-atomicity-in-postgresql-a-deep-dive-into-the-a-in-acid-209a
53. *ben-thul*. http://github.com/ben-thul
54. *How Complex Systems Fail - adaptivecapacitylabs.com*. https://www.adaptivecapacitylabs.com/HowComplexSystemsFail.pdf
55. *Operating at the Sharp End: The Complexity of Human Error*. https://securityandtechnology.org/wp-content/uploads/2020/07/operatingatthesharp-2.pdf
56. *Four concepts for resilience and the implications for the ...*. https://www.sciencedirect.com/science/article/pii/S0951832015000848
57. *Dr Richard Cook: How Complex Systems Fail - Psych Safety*. https://psychsafety.com/psychological-safety-78-dr-richard-cook/
58. *Operating at the Sharp End: The Complexity of Human Error*. https://www.researchgate.net/profile/Richard-Cook-8/publication/332248963_Operating_at_the_Sharp_End_The_Complexity_of_Human_Error/links/5ca94418299bf118c4b8b217/Operating-at-the-Sharp-End-The-Complexity-of-Human-Error.pdf
59. [[PDF] Antifragile: Things That Gain from Disorder](http://kgt.bme.hu/files/BMEGT30M400/Taleb_Antifragile__2012.pdf)
60. *Antifragile Summary and Study Guide | SuperSummary*. https://www.supersummary.com/antifragile/summary/
61. *Antifragile (book) - Wikipedia*. https://en.wikipedia.org/wiki/Antifragile_(book)
62. *Antifragile: Things that Gain from Disorder - Google Books*. http://books.google.com/books/about/Antifragile.html?id=rkOUnAEACAAJ
63. *Antifragile: Things That Gain from Disorder - CPOR*. http://cpor.org/af/Taleb_Antifragile.pdf
64. *PRINCIPLES OF CHAOS ENGINEERING - Principles of chaos engineering*. https://principlesofchaos.org/
65. *Google SRE - Defining slo: service level objective meaning*. https://sre.google/sre-book/service-level-objectives/
66. [Software Architecture in Practice, 4th Edition [Book]](https://www.oreilly.com/library/view/software-architecture-in/9780136885979/)
67. *SEI Quality Model*. https://quality.arc42.org/articles/sei-quality-model
68. *(PDF) ATAM: Method for Architecture Evaluation - ResearchGate*. http://researchgate.net/publication/2814191_ATAM_Method_for_Architecture_Evaluation
69. *People — Johnson Favaro*. http://johnsonfavaro.com/people
70. *Antifragile - Things that Gain from Disorder - Broché*. http://maarifculture.com/antifragile-things-that-gain-from-disorder-nassim-nicholas-taleb/dp/9780141038223
71. *Creative Product Semantic Scale - APA PsycNet*. https://psycnet.apa.org/getdoi.cfm?doi=10.1037/t66149-000
72. *Assessing design creativity - ScienceDirect*. https://www.sciencedirect.com/science/article/pii/S0142694X11000111
73. *Uses of the novelty metrics proposed by Shah et al.: what ...*. https://www.cambridge.org/core/journals/design-science/article/uses-of-the-novelty-metrics-proposed-by-shah-et-al-what-emerges-from-the-literature/28EAA999E457B6A56C3B36AFC181890E
74. *A Pattern Language - Wikipedia*. https://en.wikipedia.org/wiki/A_Pattern_Language
75. *The timeless way of building : Alexander, Christopher, 1936 ...*. https://archive.org/details/timelesswayofbui0000alex_u9i8
76. *Notes On The Synthesis of Form | PDF | Logic | Teaching ...*. https://www.scribd.com/document/187788385/Notes-on-the-Synthesis-of-Form
77. *ATAM: Method for Architecture Evaluation | CMU Software Engineering Institute*. https://www.sei.cmu.edu/library/atam-method-for-architecture-evaluation/
78. *Designerly ways of knowing : Cross, Nigel, 1942- : Free ...*. https://archive.org/details/designerlywaysof0000cros
79. *Design Thinking: Understanding How Designers Think and Work ...*. https://www.bloomsbury.com/uk/design-thinking-9781350305069/
80. *Designerly Ways of Knowing and Thinking - Springer*. https://link.springer.com/content/pdf/10.1007/978-1-4471-7541-4.pdf
81. *Design Thinking: Understanding How Designers Think and Work*. https://www.amazon.com/Design-Thinking-Understanding-Designers-Think/dp/1847886361
82. *Architecture Tradeoff Analysis Method® - ATAM® - DTIC*. http://apps.dtic.mil/sti/tr/pdf/AD1087054.pdf
83. [[PDF] Cybersecurity Maturity Model Certification (CMMC)](http://sei.cmu.edu/documents/6202/Cybersecurity-Maturity-Model-Certification-CMMC_oeH9RY6.pdf)
84. *(PDF) The Architecture Tradeoff Analysis Method. - ResearchGate*. https://www.researchgate.net/publication/221473740_The_Architecture_Tradeoff_Analysis_Method
85. *Developer Tool Sprawl: 14-Tool Chaos Costs 40% ...*. http://byteiota.com/developer-tool-sprawl-14-tool-chaos-costs-40-productivity
86. *How Google onboarding improved developer productivity*. https://www.devpath.com/blog/google-developer-productivity
87. *Software solutions for newcomers’ onboarding in software ...*. https://www.sciencedirect.com/science/article/pii/S0950584924001733
88. *Developer Onboarding Best Practices | Practical Guide*. https://document360.com/blog/developer-onboarding-best-practices/
89. *Learning Center - Swimm*. http://swimm.io/learn
90. *OnBoardAI — AI-Powered Developer Onboarding Software*. https://www.onboard-developer.com/
91. *What is developer experience? | Atlassian*. https://www.atlassian.com/developer-experience
92. *Survey reveals AI’s impact on the developer experience*. https://github.blog/news-insights/research/survey-reveals-ais-impact-on-the-developer-experience/
93. *Welcoming Optic, an API documentation and management tool, to Atlassian - Inside Atlassian*. http://atlassian.com/blog/announcements/optic-acquisition
94. *Developer Experience Lab - Microsoft Research*. https://www.microsoft.com/en-us/research/group/developer-experience-lab/
95. *Revolutionizing Newcomers’ Onboarding Process in OSS ...*. https://arxiv.org/pdf/2505.04277
96. *A Case Study of Onboarding in Software Teams: Tasks and ...*. https://arxiv.org/pdf/2103.05055
97. *Catharsis Consulting — Cat Hicks, PhD*. http://catharsisinsight.com/
98. *DX: Developer Intelligence Platform*. http://move-dx.com/
99. *What Improves Developer Productivity at Google? Code Quality.*. https://research.google/pubs/what-improves-developer-productivity-at-google-code-quality/
100. *Joseph Atkins-Turkish - Founding Software Engineer at ...*. http://linkedin.com/in/joseph-atkins-turkish-47559275
101. *Ciera Jaspan - Google Research*. https://research.google/people/cierajaspan/
102. *Agentic Code Review & Developer Productivity Platform*. http://getoptimal.ai/old-home
