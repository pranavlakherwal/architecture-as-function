# Defensible Measurement Procedures for Nine Architectural Cost Axes

## Executive Summary

- **Findability Has a Formal IR Metric**: Sinha et al. (2023) define findability as f(d) = (1/|Q_d|) * sum(xi(p_dq, c)), a user-oriented metric distinct from retrievability, validated on TREC and MS MARCO benchmarks -> Adapt this formula to repository search by treating files as documents and developer queries as information needs.
- **Change Impact Analysis Covers 111 Methods**: Kretsou et al. (2021) systematically mapped 111 CIA papers, finding that indirect coupling metrics are "highly correlated to maintenance and testing effort" across seven open-source systems -> Use afferent/efferent coupling as a passive proxy for c_modify.
- **Developer Onboarding Now Has a Quantitative Benchmark**: DX research across six multinational enterprises established the 10th pull request as an onboarding milestone, with AI-assisted developers reaching it in 49 days versus 91 days for non-users -> Adopt "time to 10th PR" as the operational definition of c_onboard productivity.
- **Architectural Drift Is Measurable but Inherently Retrospective**: Software entropy increases in approximately 76% of open-source projects studied (n=158), with a median cross-correlation lag of 7-10 weeks between project activity changes and entropy shifts -> c_drift requires a trailing-window measurement design; real-time prediction remains research-grade.
- **FAIR v3.0 Provides a First-Principles Risk Decomposition**: The FAIR standard decomposes loss event frequency into Contact Frequency x Probability of Action x Susceptibility, enabling quantitative c_loss estimation in financial terms -> Map repository events (overwrites, orphans, dead links) to FAIR's threat-event taxonomy for defensible probability estimates.
- **FinOps Unit Economics Directly Addresses c_money**: The FinOps Foundation's cloud unit economics framework defines cost-per-core-hour, cost-per-GB-RAM, and cost-per-transaction as standard measurement units -> Attribute architecture-specific costs by tagging cloud resources to repository structure.
- **Software Entropy Correlates Moderately with Project Evolution**: Mannan et al. (2020) found median cross-correlations of 0.45 (methods), 0.36 (developers), and 0.35 (files) with Shannon entropy across 158 projects -> Entropy is a cheap, per-file proxy but not a strong standalone predictor for any single cost axis.
- **Incremental Build Research Quantifies c_derive**: McIntosh (MSR 2024) documents how cold CI builds in ephemeral containers render incremental builds "inert," making full regeneration the default -> Measure c_derive as wall-clock time of full rebuild minus incremental rebuild, tracked from CI logs.
- **Three Axes Require Fresh Invention**: c_reverse, c_loss, and c_derive lack direct published measurement procedures and require hybrid or novel designs, making them the highest-uncertainty axes in the framework.
- **Passive Measurement Can Cover Seven of Nine Axes**: Git log mining, filesystem scanning, and CI log parsing yield usable signals for all axes except c_find and c_onboard, which require at minimum semi-active instrumentation (search-query logging, PR timestamp tracking).

---

## The Nine-Axis Measurement Framework: Summary Table

| Axis | (a) Published Procedures | (b) Units | (c) Key Confounders | (d) Status | (f) Difficulty |
|------|-------------------------|-----------|---------------------|------------|----------------|
| c_find | Sinha et al. findability metric [IR]; Sadowski et al. code search [SE]; Pirolli information foraging [HCI]; APQC search success rate [KM] | seconds-per-task | User expertise, query formulation skill, search tool quality, familiarity with repo | HYBRID | 3 |
| c_modify | Kretsou et al. CIA survey [SE]; Almugrin et al. coupling metrics [SE]; COCOMO II [SE]; ISO 25010 maintainability [SE Standards] | person-minutes-per-change | Change complexity, developer skill, dependency depth, test coverage, tooling | LITERATURE | 2 |
| c_storage | FinOps unit economics [Cloud Economics]; AWS S3 cost analysis [Cloud Economics] | bytes (GB) | Compression, deduplication, derived-view ratio, archive policies, storage class | LITERATURE | 1 |
| c_money | FinOps cloud unit economics [Cloud Economics]; DORA metrics [DevOps] | USD-per-month | Multi-tenancy attribution, shared infrastructure, pricing model changes, discount tiers | LITERATURE | 2 |
| c_onboard | Tacho/DX 10th PR metric [DevEx]; AIHR time-to-productivity [HR]; SPACE framework [DevEx] | calendar-days-to-Nth-PR | Prior experience, team support, documentation quality, AI tool access, project complexity | HYBRID | 3 |
| c_drift | Murphy et al. reflexion models [SE]; Mannan et al. software entropy [SE]; Jin et al. metric forest [SE]; Besker et al. ATD model [SE] | delta-integrity-score-per-week | Refactoring activity, team size changes, feature velocity, measurement interval | HYBRID | 4 |
| c_reverse | DORA Failed Deployment Recovery Time [DevOps]; git revert [Version Control]; Statsig rollback cost [DevOps] | minutes-per-undo + probability-of-side-effect | Operation type, dependency graph complexity, VCS history depth, test coverage | INVENT | 4 |
| c_loss | FAIR v3.0 loss event frequency [Risk Mgmt]; Link rot half-life studies [Archival Science]; NARA risk framework [Archival Science] | events-per-artifact-per-month | Repository size, link density, contributor churn, automation coverage | HYBRID | 4 |
| c_derive | McIntosh incremental builds [SE]; Materialized view maintenance [Database Systems] | seconds-per-regeneration + USD-per-regeneration | Dependency graph size, cache hit rate, CI environment (cold vs warm), artifact type | INVENT | 3 |

The table reveals a clear gradient: storage and money are directly measurable from infrastructure telemetry (difficulty 1-2), while drift, reverse, and loss require composite metrics assembled from multiple signals (difficulty 4). The two INVENT axes - c_reverse and c_derive - lack any single published procedure that maps directly to the axis definition.

---

## c_find: Locating Artifacts in Repository Architectures

### Published Measurement Procedures

The most rigorous framework comes from information retrieval. Sinha, Mall, and Roy (2023) define **findability** as f(d) = (1/|Q_d|) * sum(xi(p_dq, c)), where xi is a "convenience function" modeling user willingness to explore search results up to a rank threshold c. Two specific convenience functions are validated: exponential decay xi = e^(-(p-1)/3) and the inverse law xi = 1/p. The metric is validated on TREC Robust and MS MARCO benchmarks using BM25, LM-Dir, and DFR-PL2 retrieval models, with parameters including average query length k=4 and rank tolerance c=100 (Sinha et al., 2023 [6]). Mean Findability and Findability Bias (quantified via the Gini coefficient) provide system-level aggregates.

From software engineering, Sadowski et al. at Google documented how developers search for code, establishing that developers perform code searches many times per day as a core workflow activity (Sadowski et al., 2015 [73]). Stolee et al. (2025) revisited this a decade later, finding that search behaviors have shifted significantly with more complex queries and diverse tool usage (Stolee et al., 2025 [9]). Pirolli and Card's **Information Foraging Theory** from cognitive science models developer navigation as following "information scents" - patches of high-value cues that guide exploration (Pirolli, 2011 [71]). APQC's knowledge management metrics track search success rate and search frequency as organizational-level findability indicators (APQC [8]).

### Proposed Measurement Design

**Units**: seconds-per-task (for timed known-item retrieval tasks) or findability score (0-1 continuous, using the Sinha et al. formula).

**Confounders**: User expertise level, familiarity with the specific repository, query formulation ability, search tool quality (IDE search vs. grep vs. GitHub search), file naming conventions, and directory depth. The Sinha et al. metric controls for query variability by averaging across a query set Q_d, but the query generation strategy itself ("popular+discriminative" term selection) may not transfer directly to repository search contexts.

**Status**: HYBRID. The IR findability metric requires adaptation: repository "documents" are files/folders, "queries" must be synthesized from realistic developer information needs, and the convenience function parameters need calibration against repository search tools rather than web search engines. **Limitation**: The metric captures search-result-rank findability but not the cognitive cost of understanding whether a found artifact is the correct one.

---

## c_modify: Measuring the Cost of Planned Changes

### Published Measurement Procedures

Change Impact Analysis (CIA) is the most mature literature. Kretsou et al. (2021) systematically mapped **111 primary studies**, finding that CIA benefits span corrective, perfective, preventive, and adaptive maintenance. They identify a critical gap: "There is a need to provide direct metrics for the quantification of CIA parameters" - most existing metrics are indirect proxies (Kretsou et al., 2021 [25]).

Almugrin, Albattah, and Melton (2016) developed indirect coupling metrics based on Martin's package design principles. **Afferent coupling** (Ca) measures import links and responsibility; **efferent coupling** (Ce) measures export links and dependency. These predict maintenance effort: in experiments across seven open-source systems (including Tomcat and Hadoop), the new metrics were "highly correlated to maintenance and testing effort," with package maintenance measured as the number of changes over time. Variables included REVISION count, package size, and revised lines of code (RLOC), all log-transformed (Almugrin et al., 2016 [23]).

COCOMO II provides macro-level estimation via Effort = a x (KLOC)^b, with an Effort Adjustment Factor (EAF) derived from fifteen cost drivers (Boehm, COCOMO [21]). ISO/IEC 25010:2023 defines maintainability as a quality characteristic with sub-characteristics including modularity, reusability, analyzability, modifiability, and testability (ISO 25010:2023 [13]).

### Proposed Measurement Design

**Units**: person-minutes-per-change, decomposed into (a) time to locate dependencies, (b) time to apply modification, (c) time to verify no regressions.

**Confounders**: Change complexity (single-file edit vs. cross-cutting concern), developer expertise, test suite coverage (higher coverage increases verification time but reduces risk), dependency graph density, and whether the change is in a hotspot (frequently modified) file.

**Status**: LITERATURE. Multiple validated approaches exist, though none provides a single "c_modify score" - assembly is required. Coupling metrics serve as the strongest passive proxy, measurable from static analysis without user instrumentation.

---

## c_storage: Bytes Occupied by Architecture

### Published Measurement Procedures

The FinOps Foundation's Cloud Unit Economics framework provides the most actionable methodology. It defines **cost-per-stored-item** as often more meaningful than cost-per-GB because the latter may not reflect savings from compression (FinOps, 2024 [46]). AWS provides tooling for analyzing S3 API operations, enabling measurement of storage costs attributable to specific API call patterns (PUT, COPY, POST, GET) (AWS S3 Cost Analysis [48]).

**Units**: bytes (GB or TB) for raw measurement; cost-per-stored-artifact for normalized comparison.

**Confounders**: Compression ratios, deduplication (especially in git packfiles), derived-view-to-source ratio, archive/cold-storage policies, git history depth (shallow clones vs. full history), and binary asset management (LFS vs. in-repo).

**Status**: LITERATURE. Direct measurement via `du`, `git count-objects`, cloud billing APIs. This is the most trivially measurable axis. **Difficulty: 1.**

---

## c_money: Dollar Cost of Operating the Architecture

### Published Measurement Procedures

The FinOps Cloud Unit Economics framework is the authoritative industry standard. It categorizes metrics into three layers: **technical** (cost per core-hour, cost per GB RAM), **financial** (contribution margin, Customer Lifetime Value), and **business** (cost per weekly active user, cost per million transactions) (FinOps, 2024 [46]). The framework emphasizes that marginal cost - the cost of one additional unit of business activity - is the key metric for optimization.

DORA metrics complement this by measuring the delivery pipeline's efficiency: Deployment Frequency, Change Lead Time, Failed Deployment Recovery Time, and Change Fail Rate. The fifth metric, Deployment Rework Rate, tracks unplanned deployments from production incidents (DORA, 2024 [65]). High-performing teams excel on all five simultaneously rather than trading speed for stability.

**Units**: USD-per-month, decomposed into storage fees, API call fees, CI/CD compute costs, and persistence-layer costs.

**Confounders**: Multi-tenancy (shared infrastructure makes attribution difficult), reserved-instance vs. on-demand pricing, discount tiers, regional pricing variation, and the boundary problem (what counts as "architecture cost" vs. "application cost").

**Status**: LITERATURE. Cloud billing APIs, CI/CD platform cost reports, and resource tagging provide direct measurement. The main challenge is attribution, not measurement. **Difficulty: 2.**

---

## c_onboard: Time for New Contributors to Become Productive

### Published Measurement Procedures

The most concrete empirical benchmark comes from DX research. Laura Tacho analyzed data from **six multinational enterprises** and measured how quickly new hires reached their **10th pull request** - "an established metric for tracking ramp-up time." Engineers using AI daily reached this milestone in **49 days** versus **91 days** for non-AI users. Weekly AI users took 73.5 days; monthly users took 84 days (Tacho/DX, 2025 [44]).

AIHR defines Time to Productivity (TTP) as the date of full productivity minus the employee's start date, distinguishing it from Time to Proficiency (mastery of advanced skills) (AIHR [45]). The SPACE framework captures onboarding under its "Efficiency and Flow" dimension, measuring handoffs and delays in a process (Forsgren et al., SPACE [2]). Cognitive Load Theory, applied to developer experience, emphasizes that intrinsic complexity of the architecture directly impacts onboarding time (Cognitive Load + DevEx [41]).

### Proposed Measurement Design

**Operational definition of "productive"**: A contributor is productive when they have merged their Nth non-trivial pull request (recommended N=10 based on DX research) or when they can complete a standardized task set without assistance. For AI agents, "productive" means successfully executing an end-to-end modification workflow (find artifact, modify, verify, commit) with less than 20% error rate.

**Units**: calendar-days-to-Nth-PR.

**Confounders**: Prior experience with the technology stack, quality of documentation, team mentoring intensity, AI tool access, project complexity, and PR size distribution (small fix PRs vs. feature PRs).

**Status**: HYBRID. The 10th PR metric is validated in industry but requires adaptation for the architecture-specific context (onboarding to a repository structure vs. to a team). **Difficulty: 3.**

---

## c_drift: Rate of Architectural Integrity Decay

### Published Measurement Procedures

Murphy, Notkin, and Sullivan (1995) introduced **reflexion models** that compare a high-level architectural model against source code, classifying relationships as convergences (matches), divergences (unexpected dependencies), or absences (missing expected dependencies). The approach was demonstrated on NetBSD (250,000 lines of C) in "only a few hours" (Murphy et al., 1995 [75]). This remains the foundational approach for architecture conformance checking.

Mannan et al. (2020) studied **software entropy** evolution across **158 open-source Java projects**, finding that **76% showed statistically significant increasing entropy trends**. Shannon entropy H(X) = -sum(P(x_i) * log2(P(x_i))) is computed per-file and aggregated weekly. Median cross-correlations with project metrics were: **0.45 (total methods), 0.36 (active contributors), 0.35 (total files)**. The average lag was **7.48 to 10.51 weeks**, meaning project activity changes precede entropy shifts (Mannan et al., 2020 [60]). Jin et al. (2023) extended this with a **Metric Forest Structure** that links implementation-level metrics to architectural decay patterns (Jin et al., 2023 [17]).

Besker, Martini, and Bosch (2018) modeled Architectural Technical Debt using **principal** (remediation cost) and **interest** (ongoing extra effort), finding developers waste an average of **23% of their time** due to technical debt, with maintenance consuming **50-70% of total effort** (Besker et al., 2018 [14]).

### Proposed Measurement Design

**Units**: delta-integrity-score-per-week, where the integrity score is a composite of (a) reflexion model divergence count, (b) Shannon entropy, and (c) coupling metric drift from baseline.

**Confounders**: Active refactoring (which temporarily increases entropy before reducing it), team size changes, feature velocity, and the "measurement disturbs the system" problem - knowing drift is measured changes behavior.

**Status**: HYBRID. Reflexion models and entropy are well-published but must be composed into a single drift rate metric. The key limitation is that reflexion models require a human-defined high-level model as input. **Difficulty: 4.**

---

## c_reverse: Cost of Undoing Mistaken Operations

### Published Measurement Procedures

DORA's **Failed Deployment Recovery Time** (replacing the older MTTR) measures the time to restore service after a failed deployment, serving as the closest standardized metric (DORA, 2024 [65]). Git revert creates an inverse commit that maintains full history, providing a mechanical undo capability, but the documentation focuses on procedure rather than cost measurement (Git Revert [27]).

Statsig's analysis of rollback costs identifies "decreased team morale and thousands of lost engineering hours" as hidden costs, emphasizing that "without solid metrics, you're left guessing the reasons behind failures" (Statsig, 2026 [26]). The Industry Analyst documents that "reversibility introduces new layers of cost, complexity, and risk that are often invisible at decision time" in infrastructure contexts (TIA Research [28]).

### Proposed Measurement Design

**Units**: composite of minutes-to-complete-undo + probability-of-side-effect (0-1).

**Proposed procedure**: (1) Classify operations into types (file move, deletion, rename, restructure). (2) For each type, measure: time to identify affected dependencies (from git log analysis), time to execute reversal, and number of downstream artifacts requiring update. (3) Risk component estimated from historical revert-then-fix-forward frequency in git log.

**Confounders**: Operation type (rename is low-risk, restructure is high-risk), dependency graph density, test coverage, VCS history depth, and whether the operation has been propagated to downstream consumers.

**Status**: INVENT. No published procedure directly measures "cost of undoing a file move." DORA's recovery time is the closest analog but targets deployment failures, not file-level operations. **Limitation**: The risk component is inherently probabilistic and can only be calibrated from historical incident data. **Difficulty: 4.**

---

## c_loss: Probability of Artifact Misplacement or Corruption

### Published Measurement Procedures

The **FAIR Standard v3.0** (January 2025) provides the most rigorous framework. It decomposes risk into Loss Event Frequency (LEF) = Threat Event Frequency (TEF) x Susceptibility. TEF itself decomposes into Contact Frequency (CF) x Probability of Action (PoA). Loss Magnitude splits into Primary Loss and Secondary Loss, with six forms of loss: productivity, response costs, replacement costs, fines/judgments, reputation damage, and competitive advantage loss (FAIR v3.0%20Standard%20v3.0%20(January%202025).pdf)).

From archival science, link rot studies provide empirical baselines: a 2002 study found approximately **3% of digital library objects became inaccessible after one year**, equating to a half-life of approximately 23 years. On the general web, approximately **1 link per 200 breaks each week**. A 2023 Million Dollar Homepage study found 28% of links returned errors, 45% were redirected, and only 27% loaded directly (Link Rot, Wikipedia [38]). NARA's Digital Preservation Framework provides format-level risk assessment with risk matrices for over 700 file formats (NARA [58]).

### Proposed Measurement Design

**Units**: events-per-artifact-per-month (misplacement, overwrite, orphan, dead-link counted separately).

**Proposed procedure**: (1) Scan for orphan files (files not referenced by any other artifact) using tools like OrphanHunter (OrphanHunter [39]). (2) Parse git log for overwrite events (same file path modified by different authors within a short window). (3) Validate internal links/references for dead-link detection. (4) Compute event frequency per artifact per time window using FAIR's LEF decomposition.

**Confounders**: Repository size (larger repos have more surface area), contributor churn rate, automation coverage (CI checks catch some events), and the detection problem - undetected losses are by definition unmeasured.

**Status**: HYBRID. FAIR provides the probability framework but targets cybersecurity threats; adaptation to repository artifact events requires mapping the FAIR taxonomy to file-level operations. Link rot baselines from archival science provide calibration data. **Difficulty: 4.**

---

## c_derive: Cost of Regenerating Derived Views

### Published Measurement Procedures

McIntosh (MSR 2024) documents the fundamental tension: incremental builds traverse dependency graphs and invoke only affected commands, but modern CI pipelines using ephemeral containers start from "cold" builds, "rendering the incremental builds inert." This makes full regeneration the default cost (McIntosh, 2024 [31]). Build specifications (Makefiles, CMakeLists.txt) declare dependencies that dictate command ordering, and "underspecified build systems" with missing dependency expressions cause sporadic failures during parallel execution.

From database systems, **materialized view maintenance** provides the theoretical foundation: when a source relation changes, derived views must be updated. The cost depends on the view definition complexity and the change's scope. Materialize provides real-time incremental view maintenance as a commercial implementation (Materialize [35]). Cache invalidation architecture for enterprise systems documents event-driven invalidation strategies that avoid expensive full rebuilds (PathToProject, 2026 [34]).

### Proposed Measurement Design

**Units**: seconds-per-regeneration (time) + USD-per-regeneration (cost), measured per derived-view type.

**Proposed procedure**: (1) Enumerate derived views (indexes, caches, embeddings, summaries, compiled outputs). (2) For each, trigger regeneration after a single-source-file change and measure wall-clock time and compute cost from CI billing. (3) Compare full-rebuild time vs. incremental time (if available). (4) Weight by change frequency from git log.

**Confounders**: Cache warm/cold state, CI environment specs (CPU, memory), parallelism degree, dependency graph completeness, and artifact type heterogeneity.

**Status**: INVENT. Build-system literature measures build time but not the broader category of "derived views" (embeddings, summaries). Database materialized-view maintenance provides the theory but no direct repository-applicable procedure. **Limitation**: The derived-view inventory must be manually defined - there is no automated way to discover all derived artifacts in an arbitrary repository. **Difficulty: 3.**

---

## Task 10: Fundamentally Retrospective or Non-Measurable Axes

Three axes present fundamental temporal measurement challenges:

**c_drift is inherently retrospective.** Architectural integrity decay can only be quantified after it has occurred. Mannan et al. (2020) found an average lag of **7.48-10.51 weeks** between project activity changes and entropy shifts, meaning drift is detected well after the causal events. Reflexion model divergences accumulate silently until someone runs the conformance check. The implication is that c_drift cannot be measured in real-time; it requires a trailing-window design (e.g., compare integrity score at t versus t-4 weeks). Continuous integration of drift detection tools like Erode (Erode [16]) can reduce the measurement lag but not eliminate it.

**c_loss has a detection asymmetry.** By definition, undetected losses are unmeasured. The FAIR model acknowledges this by treating loss frequency as a probabilistic estimate rather than a census. Link rot studies demonstrate that decay rates vary by context (3% per year in curated digital libraries vs. approximately 25% per year on the open web). For repository artifacts, the true loss rate is always greater than or equal to the detected rate, creating a systematic undercount. Retrospective discovery (finding orphans or dead links during a periodic audit) is the only way to approximate the true rate.

**c_reverse has a counterfactual problem.** The "risk" component of c_reverse asks: what would have gone wrong if the undo had been imperfect? This is inherently counterfactual and can only be estimated from historical incident data. A repository with no history of failed reversals has no data to calibrate risk, yet the risk is not zero.

**c_find is measurable in real-time** but only under controlled conditions (user studies with timed tasks). Passive measurement of findability requires search query logs, which many repositories do not generate.

---

## Task 11: Sub-Architecture Structural Proxies and Their Correlations

### Tree-Level Metrics

| Proxy Metric | Computation | Measurable Per-File/Folder | Known Correlations |
|---|---|---|---|
| Shannon entropy | H(X) = -sum(P(x_i) log2 P(x_i)) per file | Yes (per-file, aggregate to project) | Moderate: 0.45 with total methods, 0.36 with contributors, 0.35 with files (Mannan et al., 2020) |
| Directory depth | Max/mean path length from root | Yes (per-file) | Hypothesized proxy for c_find (deeper = harder to navigate); no direct empirical validation found |
| Branching factor | Mean children per directory node | Yes (per-folder) | Hypothesized proxy for c_find; high branching increases visual scanning cost |
| Afferent coupling (Ca) | Count of inbound dependency links per package | Yes (per-package/folder) | "Highly correlated to maintenance effort" (Almugrin et al., 2016) |
| Efferent coupling (Ce) | Count of outbound dependency links per package | Yes (per-package/folder) | Correlated to testing effort and change propagation (Almugrin et al., 2016) |
| Code churn | Lines added + deleted per file per time period | Yes (per-file) | Proxy for c_modify (high-churn files need frequent changes); tracked by git analytics tools |
| File age / staleness | Time since last modification | Yes (per-file) | Potential proxy for c_loss (stale files more likely to be orphaned) and c_drift (unmaintained areas accumulate debt) |

Entropy stands out as the most empirically validated sub-architecture proxy. In 158 open-source projects, 76% showed statistically significant increasing trends, and the metric can be computed at the file level and aggregated upward (Mannan et al., 2020 [60]). However, the correlations are moderate (0.35-0.45), meaning entropy alone explains less than 25% of variance in project evolution metrics. Coupling metrics (Ca, Ce) have stronger predictive validity for c_modify specifically but require dependency analysis tools rather than simple filesystem scanning.

**Key gap**: No published study directly correlates directory depth or branching factor with any of the nine cost axes. These remain theoretically motivated proxies awaiting empirical validation.

---

## Task 12: Passive vs. Active Measurement Strategies

### Passive Measurement (No User Instrumentation Required)

| Signal Source | Measurable Axes | Method |
|---|---|---|
| git log | c_modify (churn, change frequency), c_drift (entropy over time), c_loss (overwrite patterns), c_onboard (time to Nth commit/PR), c_reverse (revert frequency) | Parse commit history for file-level change patterns, author timelines, revert commits |
| Filesystem scan | c_storage (du, file counts), c_find (depth, branching), c_loss (orphan detection), c_drift (staleness analysis) | Walk directory tree; compute structural metrics; scan for unreferenced files |
| CI/CD logs | c_money (compute time, build costs), c_derive (build duration, cache hit rates), c_reverse (rollback frequency) | Parse build timestamps, resource usage, deployment events |
| Dependency manifests | c_modify (coupling analysis), c_drift (dependency freshness) | Parse package.json, requirements.txt, Makefile for dependency graphs |
| Cloud billing APIs | c_money (direct costs), c_storage (storage tier costs) | Query AWS Cost Explorer, GCP Billing, Azure Cost Management |
| Internal link scanning | c_loss (dead link detection) | Crawl markdown links, import statements, config references for broken targets |

Git analytics tools like Axify track commits, PRs, cycle time, and rework rate, but warn that "relying too heavily on Git-based metrics without context can result in misleading insights and even incentivize the wrong behaviors" (Axify, 2025 [54]). The SPACE framework researchers similarly caution against using activity metrics in isolation.

### Active Measurement (Requires User Studies or Instrumentation)

| Method | Measurable Axes | Requirement |
|---|---|---|
| Timed known-item retrieval tasks | c_find | Controlled user study with standardized search tasks |
| Modification task experiments | c_modify | Developers perform specified changes while being timed |
| Search query logging | c_find | Instrument IDE/search tool to capture queries and success/failure |
| Onboarding diary studies | c_onboard | New contributors self-report milestones over weeks |
| Architecture review sessions | c_drift | Expert panel evaluates conformance against intended design |
| Chaos engineering experiments | c_reverse, c_loss | Deliberately introduce faults and measure recovery |

The critical distinction: passive measurement yields historical patterns and structural properties, while active measurement captures the human-experienced cost that the axes ultimately represent. Passive proxies are necessary but not sufficient - they estimate what the human cost would be without directly observing it.

---

## Task 13: Minimum-Viable Passive Measurement Instrument

### Tool Design: ArchCost Analyzer

A tool that estimates all nine c_i for an arbitrary repository using passive signals only would require the following inputs and produce the following outputs:

**Required Inputs:**
1. **Git repository** (full clone with history) - for commit log, file history, revert detection, author timelines
2. **Filesystem access** (working tree) - for directory structure, file sizes, link scanning
3. **CI/CD log export** (optional but strongly recommended) - for build times, deployment events, compute costs
4. **Cloud billing data** (optional) - for direct cost attribution
5. **Dependency manifests** (auto-detected) - package.json, requirements.txt, Makefile, etc.

**Per-Axis Estimation Strategy:**

| Axis | Passive Estimation Method | Confidence |
|---|---|---|
| c_find | Directory depth + branching factor + naming entropy; calibrated against findability benchmarks | Low (no direct validation) |
| c_modify | Coupling analysis from imports/dependencies + historical churn rate + mean change-set size from git log | Medium |
| c_storage | du -sh + git count-objects --size-pack + enumerate derived artifacts | High |
| c_money | CI log compute-hours x unit cost + cloud billing tagged to repo | High (if billing data available) |
| c_onboard | Time-to-Nth-commit for historical new contributors extracted from git log | Medium |
| c_drift | Shannon entropy trend over sliding 4-week windows + dependency freshness score | Medium |
| c_reverse | Historical revert frequency + mean revert-to-fix-forward ratio + dependency fan-out of reverted files | Low-Medium |
| c_loss | Orphan file count + dead internal link count + overwrite collision rate from git log | Medium |
| c_derive | CI build time after single-file changes (from CI log) + derived artifact enumeration | Medium (if CI logs available) |

**Architecture:**
The tool would run as a CLI that (1) clones or accesses the repo, (2) walks the filesystem computing structural metrics, (3) parses the full git log extracting temporal patterns, (4) performs static dependency analysis, (5) optionally ingests CI and billing data, and (6) produces a JSON report with estimated c_i values, confidence intervals, and data-quality flags for each axis.

**Critical limitations**: c_find and c_reverse estimates from passive signals alone have low confidence because they are fundamentally about human-experienced costs that structural proxies can only approximate. The tool should flag these axes as "requires active validation" in its output.

---

## Synthesis: Cross-Cutting Patterns and Measurement Trade-offs

Three fundamental tensions emerge across the nine axes.

**The passive-active gap.** Axes that measure human-experienced costs (c_find, c_modify, c_onboard, c_reverse) are best measured through active user studies but most practically estimated through passive proxies. The correlation between passive proxies and actual human costs is moderate at best (r = 0.35-0.45 for entropy, "highly correlated" but unquantified for coupling metrics). This means any passive-only measurement instrument systematically trades validity for feasibility. Organizations should use passive measurement for continuous monitoring and periodic active measurement for calibration.

**The retrospective-prospective divide.** c_drift, c_loss, and c_reverse are inherently backward-looking: drift can only be measured after it has occurred, losses after they are detected, and reversal costs after reversals are attempted. Prospective estimation requires either simulation (computationally expensive) or extrapolation from historical rates (assumes stationarity). The 7-10 week lag identified by Mannan et al. (2020) for entropy means that even "real-time" drift monitoring is actually detecting changes that began two months earlier.

**The attribution boundary problem.** c_money and c_storage require clear boundaries around what constitutes "the architecture" versus "the application." In cloud environments with shared infrastructure, multi-tenancy makes per-architecture attribution approximate rather than exact. The FinOps framework addresses this with resource tagging, but tagging coverage is typically incomplete. Similarly, c_derive depends on a complete inventory of derived artifacts, which no automated tool can fully enumerate.

Comparing measurement maturity across the nine axes reveals that infrastructure-observable axes (c_storage, c_money) are essentially solved problems with direct measurement from billing APIs and filesystem tools. Process-observable axes (c_modify, c_onboard, c_drift) have strong published frameworks requiring assembly. Human-experience axes (c_find, c_reverse) and probabilistic axes (c_loss) remain the frontier, requiring either fresh invention or careful adaptation of adjacent-field frameworks. The gap between the best-understood axis (c_storage, difficulty 1) and the least-understood (c_reverse, difficulty 4) represents roughly a decade of measurement-science maturity.

---

## Measurement Risks: Where Uncertainty Is Highest

| Axis | Risk Level | Primary Source of Uncertainty |
|---|---|---|
| c_reverse | **Very High** | No published measurement procedure; risk component is counterfactual; no passive signal directly measures undo cost |
| c_loss | **Very High** | Detection asymmetry (undetected losses are unmeasured); FAIR adaptation to file-level events is untested; base rates vary by orders of magnitude across contexts |
| c_drift | **High** | Requires human-defined architectural model for reflexion analysis; entropy is a moderate proxy (r < 0.5); 7-10 week measurement lag |
| c_find | **High** | Passive proxies (depth, branching) lack empirical validation against actual search times; active measurement requires costly user studies |
| c_onboard | **Medium** | 10th PR metric is validated but coarse; does not distinguish architecture-specific onboarding from general team onboarding; confounded by mentoring quality |
| c_derive | **Medium** | Derived artifact inventory must be manually defined; cold vs. warm CI state creates measurement noise; heterogeneous artifact types resist single-metric aggregation |
| c_modify | **Low-Medium** | Coupling metrics are validated but indirect; change complexity varies enormously; task decomposition (find + modify + verify) complicates single-number reporting |
| c_money | **Low** | Attribution boundary is the main challenge; direct measurement is available when billing data is accessible |
| c_storage | **Very Low** | Direct measurement via filesystem tools; primary uncertainty is in defining what to include (history, LFS, derived views) |

The two highest-risk axes - c_reverse and c_loss - share a common characteristic: they measure events that are rare, consequential, and partially unobservable. This is precisely the domain where the FAIR standard's probabilistic approach adds the most value, but also where calibration data is scarcest. Organizations adopting this measurement framework should invest disproportionate validation effort on these two axes and accept wider confidence intervals in their estimates.

---

## References

1. *The SPACE of Developer Productivity.docx*. http://coursehero.com/file/252817886/The-SPACE-of-Developer-Productivitydocx
2. *SPACE Framework: How to Measure Developer Productivity - Codacy*. https://blog.codacy.com/space-framework
3. *Developer experience research methods: a complete guide for ...*. https://cleverx.com/guides/developer-experience-research-methods-a-complete-guide-for-product-and-ux-teams/
4. *Addison Hiles - Developer Productivity & AI Enablement ...*. http://linkedin.com/in/devexgirl
5. *Best Employee Onboarding Software 2026*. http://theworkademy.com/employee-onboarding-software
6. *Findability: A Novel Measure of Information Accessibility*. https://arxiv.org/pdf/2310.09508v1
7. *IKM TeckChek*. http://linkedin.com/company/teckchek
8. *Knowledge Management Metrics | APQC*. https://www.apqc.org/resources/blog/knowledge-management-metrics
9. *10 Years Later: Revisiting How Developers Search for Code*. https://kstolee.github.io/assets/papers/stolee2025FSE.pdf
10. *Findability and Information Architecture Primer | Information ...*. https://www.informationarchitected.com/resources/whitepapers/findability-and-information-architecture-primer/
11. *Accelerate Modernization with Architectural Observability*. http://vfunction.com/blog/architectural-observability-accelerates-app-modernization
12. *ISO/IEC 25010:2011 - Systems and software engineering*. http://iso.org/standard/35733.html
13. *ISO/IEC 25010:2023 (en), Systems and software engineering ...*. https://www.iso.org/obp/ui#!iso:std:iso-iec:25010:ed-2:v1:en
14. *Managing architectural technical debt: A unified model and ...*. https://www.sciencedirect.com/science/article/pii/S0164121217302121
15. *Quality Metrics in Software Architecture | IEEE Conference ...*. https://ieeexplore.ieee.org/document/10092705
16. *Erode - Architecture Drift Detection for Code Changes*. https://erode.dev/
17. *Identifying Code Changes for Architecture Decay via a Metric ...*. https://ieeexplore.ieee.org/document/10207153
18. *Real-Time Reflexion Modelling in architecture reconciliation ...*. https://www.sciencedirect.com/science/article/pii/S0950584915000270
19. *Terms of Service*. http://mault.ai/terms
20. *Drift Detection — Archiet*. https://archiet.com/features/drift-detection
21. *COCOMO Model: Formula, Types, and Cost Estimation*. https://www.datacamp.com/tutorial/cocomo-model
22. *A multi-level measures-driven change impact analysis approach ...*. https://link.springer.com/article/10.1007/s11334-025-00614-4
23. *Using indirect coupling metrics to predict package ...*. https://www.sciencedirect.com/science/article/pii/S016412121600056X
24. *COCOMO Model - Software Engineering - GeeksforGeeks*. https://www.geeksforgeeks.org/software-engineering/software-engineering-cocomo-model/
25. *Change impact analysis: A systematic mapping study*. https://www.sciencedirect.com/science/article/pii/S016412122030282X
26. *The Hidden Cost of Rolling Back Without Metrics - statsig.com*. https://www.statsig.com/perspectives/rollback-costs-no-metrics-software
27. *Git - git-revert Documentation*. https://git-scm.com/docs/git-revert
28. *TIA Research-The Hidden Cost of Reversibility in ...*. https://theindustryanalyst.com/the-hidden-cost-of-reversibility-in-infrastructure-technology/
29. *Deployment Rollback: How to Measure Cost and Efficiency*. https://www.linkedin.com/advice/0/how-do-you-measure-cost-efficiency-deployment
30. *How To Revert A Commit With Git Revert? - GeeksforGeeks*. https://www.geeksforgeeks.org/git/how-to-revert-a-commit-with-git-revert/
31. *Mining Our Way Back to Incremental Builds for DevOps Pipelines*. https://rebels.cs.uwaterloo.ca/papers/msr2024_mcintosh.pdf
32. *Cache miss for the first stage of multi-stage build #1742*. http://github.com/moby/buildkit/issues/1742
33. *NXM Labs Inc.*. http://nxmlabs.com/
34. *Headless Cache Invalidation Architecture for Enterprise ...*. https://www.pathtoproject.com/blog/20260413-headless-cache-invalidation-architecture-for-enterprise-content-platforms
35. *Materialize: The Live Data Layer for Apps and AI Agents*. http://materialize.com/
36. *Factor Analysis of Information Risk (FAIR) Standard v3.0 ...*. https://www.fairinstitute.org/hubfs/Standards%20Artifacts/Factor%20Analysis%20of%20Information%20Risk%20(FAIR)%20Standard%20v3.0%20(January%202025).pdf
37. *How to find 404 pages (broken links) in GA4*. http://optimizesmart.com/how-to-find-404-pages-broken-links-in-ga4
38. *Link rot - Wikipedia*. https://en.wikipedia.org/wiki/Link_rot
39. *GitHub - Hazardous-God/orphanhunter: Your web project a ...*. https://github.com/Hazardous-God/orphanhunter
40. *American Express · GitHub*. http://github.com/americanexpress
41. *Managing Developer Cognitive Load and Team Topologies: A ...*. https://www.youngju.dev/blog/devops/2026-03-14-developer-cognitive-load-devex-team-topology.en
42. *How to Read a Study Record | ClinicalTrials.gov*. http://clinicaltrials.gov/study-basics/how-to-read-study-record
43. *ZoomInfo's Developer-Centric Productivity Transformation*. http://engineering.zoominfo.com/powering-innovation-zoominfos-developer-centric-productivity-transformation
44. *AI cuts onboarding time in half for new hires in the enterprise*. https://newsletter.getdx.com/p/ai-cuts-developer-onboarding-time-in-half
45. *Time To Productivity: Definition & How to Calculate | HR Glossary*. https://www.aihr.com/hr-glossary/time-to-productivity/
46. *Introduction to Cloud Unit Economics - FinOps*. https://www.finops.org/wg/introduction-cloud-unit-economics/
47. *Upload Content (S3 Compatible)*. http://developers.preservica.com/api-reference/3-upload-content-s3-compatible
48. *Optimize storage costs by analyzing API operations on Amazon S3*. https://aws.amazon.com/blogs/storage/optimize-storage-costs-by-analyzing-api-operations-on-amazon-s3/
49. *Cloud Cost Efficiency I The Keys to AWS Optimization | S16 E2 - YouTube*. http://youtube.com/watch?v=dThoN5u3c7w
50. *FinOps roles, responsibilities, and team structure - Orb Billing*. http://withorb.com/blog/finops-roles-and-responsibilities
51. *SpoonLabs*. http://github.com/SpoonLabs
52. *Nemean Solutions, LLC's Post*. http://linkedin.com/posts/nemean-solutions_nemean-solutions-llc-and-agile-defense-form-activity-7257743414551547905-K7Ws
53. *Mining of Repositories to Understand Productivity in Remote ...*. https://link.springer.com/chapter/10.1007/978-3-031-75236-0_29
54. *Git Analytics: Challenges, Tools & Key Metrics*. https://axify.io/blog/git-analytics
55. *Software | Lunar Outpost*. http://lunaroutpost.com/software
56. *Nehemiah Security Management Team | Org Chart*. http://rocketreach.co/nehemiah-security-management_b5595894f68b02f2
57. *ThreatConnect Acquires Risk Quantification Pioneer Nehemiah Security*. http://threatconnect.com/news/threatconnect-acquires-cyber-risk-quantification-pioneer-nehemiah-security
58. *Digital Preservation Framework for Risk Assessment and ...*. https://www.archives.gov/preservation/digital-preservation/risk
59. *Nehemiah Security*. http://medium.com/%40nehemiahsecure
60. *The Evolution of Software Entropy in Open Source projects: An ...*. https://web.engr.oregonstate.edu/~sarmaa/wp-content/uploads/2020/08/Technical_Report.pdf
61. *Branching Factor - an overview | ScienceDirect Topics*. https://www.sciencedirect.com/topics/computer-science/branching-factor
62. *allenai/spoc-robot-training: SPOC: Imitating Shortest Paths ...*. http://github.com/allenai/spoc-robot-training
63. *Exploring repository architecture strategy – GitHub Well ...*. https://wellarchitected.github.com/library/architecture/recommendations/scaling-git-repositories/repository-architecture-strategy/
64. *The Thermo­dynamics of Software Entropy: Why All Code Tends ...*. https://www.javacodegeeks.com/2026/03/the-thermodynamics-of-software-entropy-why-all-code-tends-toward-disorder.html
65. *DORA's software delivery performance metrics*. http://dora.dev/guides/dora-metrics
66. *DORA metrics | Technology Radar | Thoughtworks Brazil*. http://thoughtworks.com/en-br/radar/techniques/dora-metrics
67. *Use Four Keys metrics like change failure rate to measure ...*. https://cloud.google.com/blog/products/devops-sre/using-the-four-keys-to-measure-your-devops-performance
68. *Accelerate and DORA Metrics - Software Delivery Performance ...*. https://openpracticelibrary.com/blog/accelerate-metrics-software-delivery-performance-measurement/
69. *What are DORA metrics? Complete guide to measuring DevOps ...*. http://getdx.com/blog/dora-metrics
70. *Percentage of time that developers spent on online searching*. https://www.researchgate.net/figure/Percentage-of-time-that-developers-spent-on-online-searching_fig1_315887516
71. *Information foraging as a foundation for code navigation ...*. https://dl.acm.org/doi/10.1145/1985793.1985911
72. *The Hidden Costs of AI-Generated Code in 2026*. http://codebridge.tech/articles/the-hidden-costs-of-ai-generated-software-why-it-works-isnt-enough
73. *How Developers Search for Code: A Case Study*. https://research.google.com/pubs/archive/43835.pdf
74. *Information Foraging as a Foundation for Code Navigation ...*. https://homepages.uc.edu/~niunn/papers/ICSE11-NIER.pdf
75. *Gail Murphy: Software Reflexion Models*. https://www.cs.ubc.ca/~murphy/papers/rm/fse95.html
76. *AI-Driven Drift Detection in AWS: Terraform Meets Intelligence*. https://devops.com/ai-driven-drift-detection-in-aws-terraform-meets-intelligence/
77. *Reflexion Models for State Machine Extraction and Verification*. https://ieeexplore.ieee.org/document/8530025/references
