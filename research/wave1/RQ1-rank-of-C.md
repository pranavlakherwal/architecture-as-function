# Effective Rank of a 9-Dimensional Software Architecture Cost Vector

## Executive Summary

- **Dimensional Clustering Precedent**: DORA metrics empirically cluster into two groups -- throughput (deployment frequency, lead time) and stability (change failure rate, recovery time) -- suggesting analogous clustering in architecture cost vectors is both plausible and measurable Octopus Deploy DORA Report [3] -> Expect c_find/c_modify and c_storage/c_loss to form similar clusters; design measurement studies around cluster validation.

- **Standard Dimensionality Reduction in Cost Modeling**: COCOMO II compresses 17 cost drivers into 4 categories (product, hardware, personnel, project), and its Early Design model further collapses these into 7 composite factors DataCamp COCOMO Tutorial [30] -> A 9-to-4 reduction for the cost vector C is consistent with established practice in parametric software cost estimation.

- **Architecture Erosion as Causal Root**: Architecture erosion (c_drift) causally drives increases in c_onboard, c_modify, and c_find, as eroded systems become harder to understand, navigate, and change, with practitioners reporting "enormous cost" consequences Li et al., 2021, arXiv:2103.11392 [52] -> c_drift functions as a latent driver of at least three other axes, reducing effective rank.

- **Storage-Retrieval Inverse Correlation**: Cloud storage tiering exhibits approximately 100x cost differential between hot (approximately $0.10/GB/month) and cold (approximately $0.001/GB/month) tiers, with an inverse relationship between per-byte storage cost and retrieval latency Data Lingua, 2025 [19] -> c_storage and c_find (retrieval component) are mechanistically linked through the storage tiering trade-off, collapsing one degree of freedom.

- **Quantifiable Digital Decay**: Pew Research found that **38% of webpages from 2013** were inaccessible by 2023, with **54% of Wikipedia pages** containing at least one dead reference link Pew Research, 2024 [65] -> c_loss is empirically measurable with defensible base rates; its correlation with c_storage (redundancy level) is architecturally mediated.

- **Developer Experience Three-Factor Model**: Microsoft DevEx research across 2,000+ developers found that flow state, cognitive load, and feedback loops independently predict productivity, with deep-work developers feeling **50% more productive** and those with high code understanding feeling **42% more productive** Forsgren, Microsoft Azure Blog, 2024 [72] -> c_find and c_modify both load onto the cognitive-load factor, supporting their empirical clustering.

- **Technical Debt Multi-Construct Evidence**: Comparison of SonarQube, CAST, and Squore across 50 open-source projects showed low cross-tool agreement, with archetypal analysis identifying distinct "Ruler" and "Rebel" profiles Lenarduzzi et al., 2020, Empirical Software Engineering [43] -> Technical debt is not monolithic; c_drift and c_modify capture genuinely different constructs despite surface similarity.

- **Team/Tooling Confounding**: c_onboard and c_reverse are the axes most sensitive to team practices and tooling choices (e.g., version control, documentation culture, IDE support) rather than intrinsic architectural properties SPACE Framework, ACM Queue [31] -> These two axes should be modeled with an environmental parameter to avoid conflating architecture quality with team capability.

- **Effective Rank Estimate**: Synthesizing across DORA (2 clusters), SPACE (5 dimensions with tensions), COCOMO II (17 to 4 reduction), and storage economics (inverse correlation), the effective rank has a defensible lower bound of **3** and upper bound of **6**, with practical estimate of **4-5** -> The prior hypothesis of 4-5 effective dimensions is well-supported by cross-domain evidence.

- **Minimum Sample Size for Empirical Validation**: Factor analysis with 9 variables requires 45-90 observations at the standard 5:1 to 10:1 subjects-to-variables ratio, though communality levels strongly affect this The Analysis Factor [62] -> Measuring 50 project-architecture configurations across 5-10 repositories is the minimum viable empirical study.

---

## 1. Literature Survey: Empirical Correlations Among Cost Dimensions

### 1.1 Information Retrieval Cost Models and Hick's Law (c_find)

The foundational model for c_find comes from cognitive psychology. Hick's Law establishes that reaction time scales logarithmically with the number of equally probable alternatives: **RT = a + b x log2(n)**. Empirical work on navigation design confirms that increasing a menu from 5 to 15 items produces a **58% increase in cognitive load**, and that users confronting large option sets exhibit "satisficing" behavior -- clicking the first plausible link rather than finding the optimal one Atticus Li, "Hick's Law and Navigation Design," 2026 [21]. The information scent literature further quantifies this: strong information scent in labels and headings cuts navigation time by **30-50%** and reduces failed clicks by up to **60%** UX/UI Principles, "Information Scent Law" [22].

The mechanism here is that c_find is driven by both the structural organization of artifacts (an architectural property) and the labeling/tagging quality (partly a tooling property). This dual dependency means c_find correlates with c_modify through shared architectural complexity: systems where artifacts are hard to find tend also to be systems where changes require navigating complex dependency graphs.

**Case Study -- Chunking and Hierarchical Navigation**: The Hick's Law literature demonstrates that a flat menu of 20 items is cognitively more expensive than the same 20 items organized into 4 groups of 5, because total decision time becomes proportional to log2(4) + log2(5) rather than log2(20) Atticus Li, 2026 [21]. This directly maps to software architecture: a monorepo with flat file layout imposes higher c_find than the same codebase organized into well-named modules. The chunking effect predicts that c_find should correlate with architectural modularity measures such as the number of well-defined module boundaries, which in turn affects c_modify (changes are more localized in modular systems) and c_onboard (modular systems are easier to learn).

### 1.2 DORA Metrics: Throughput-Stability Clustering

The DORA (DevOps Research and Assessment) program, surveying over **32,000 professionals**, identifies four key metrics that cluster into two groups: throughput (deployment frequency, lead time for changes) and stability (change failure rate, failed deployment recovery time) Octopus Deploy, "Understanding the 4 DORA Metrics," 2024 [3]. Multi-year research backs these metrics, and elite performers achieve on-demand deployment with less than one hour of lead time, while low performers deploy monthly with lead times exceeding six months.

This clustering is directly relevant to C. The throughput cluster maps to c_modify and c_derive (how quickly changes propagate), while the stability cluster maps to c_reverse (recovery time) and c_loss (change failure rate as a proxy for introducing defects/breakage). The DORA finding that these two clusters are empirically separable -- high throughput does not automatically guarantee high stability -- implies that the "change velocity" factor and the "change safety" factor are near-orthogonal in practice.

### 1.3 SPACE Framework: Five Interconnected Dimensions

The SPACE framework (Forsgren et al., 2021) identifies five dimensions of developer productivity: Satisfaction and well-being, Performance, Activity, Communication and collaboration, and Efficiency and flow Forsgren et al., "The SPACE of Developer Productivity," ACM Queue, 2021 [31]. Critical for our analysis, the paper explicitly notes that these dimensions are "deeply interconnected" with inherent tensions: optimizing for individual efficiency (reducing interruptions) may decrease collaboration capacity. Productivity and satisfaction are reported as "highly correlated," and maximizing flow and speed can sometimes decrease system quality.

The SPACE framework recommends capturing "at least three metrics across different dimensions" and including "at least one perceptual measure" -- advice directly applicable to measuring C. The five SPACE dimensions provide a structural analogy: if five dimensions with known correlations capture developer productivity, then 4-5 effective dimensions for a 9-axis cost vector is a defensible hypothesis.

### 1.4 Storage Tiering Economics (c_storage, c_find, c_loss)

Cloud storage economics reveal a fundamental trade-off that mechanistically links three of our nine axes. Hot storage (local SSDs) costs approximately **$0.10/GB/month** with millisecond access, standard object storage (S3, Azure Blob) sits at approximately **$0.02/GB/month**, and cold storage (S3 Glacier) costs as little as **$0.001/GB/month** but with retrieval times measured in minutes or hours Data Lingua, "Hot, Warm, Cold Data Strategies," 2025 [19]. Crucially, cold-tier retrieval fees can exceed monthly storage cost if accessed unexpectedly, and cold data is typically stored with minimal redundancy beyond basic durability Backblaze, "Cloud Storage Pricing Comparison" [16].

This creates a three-way correlation: lower c_storage -> higher c_find (retrieval latency) AND higher c_loss (reduced redundancy). The mechanism is the economic optimization of storage providers: they can offer lower prices precisely because they reduce redundancy and accept longer retrieval latencies. This is not merely correlational but structurally determined by the pricing models of AWS, GCP, and Azure.

### 1.5 Architecture Erosion Literature (c_drift, c_onboard, c_modify)

Li et al. (2021) conducted an empirical study of architecture erosion through practitioner surveys and developer community analysis, finding that erosion manifests in four ways: structural deviations (cyclic dependencies), quality degradation, maintenance difficulties, and evolution hurdles Li et al., "Understanding Architecture Erosion: The Practitioners' Perceptive," arXiv:2103.11392 [52]. Among causes, "knowledge vaporization due to staff turnover" and "lack of communication" were prominent non-technical factors. The consequence most relevant to our cost vector is that eroded architecture makes systems "significantly harder to understand and maintain," directly impacting c_onboard and c_modify.

Architecture debt -- distinguished from code-level technical debt -- can consume **up to 40% of digital transformation budgets**, with programs budgeted at $50 million reaching $70-80 million once hidden dependencies surface The New Stack, "Technical Debt vs. Architecture Debt," 2025 [51]. Furthermore, **70-80% of AI projects** reportedly fail to scale beyond pilot phase due to fragmented data platforms -- an architecture-debt phenomenon. These numbers quantify the c_money impact of c_drift.

### 1.6 Digital Preservation and Link Rot (c_loss)

Pew Research Center's 2024 study provides the most rigorous empirical data on information loss rates. Key findings: **25% of all webpages** existing between 2013-2023 were inaccessible by October 2023; **38% from 2013** specifically had disappeared; even **approximately 20% of pages from 2021** vanished within two years Pew Research, "When Online Content Disappears," 2024 [65]. For reference-intensive systems, **54% of Wikipedia pages** contain at least one dead reference link, and **11% of all Wikipedia reference links** point to non-existent pages. Social media content decays even faster: **18% of tweets** disappear within months, with 50% of eventually-removed tweets gone within **6 days**.

These rates establish a defensible empirical baseline for c_loss measurement. The Digital Preservation Coalition's risk framework categorizes loss risks by technology obsolescence, physical degradation, and organizational failure DPC, "Risks" [12], providing a taxonomy for c_loss confounders.

### 1.7 Build System Economics (c_derive)

The Kubernetes build system case study (Ranjan et al., 2025) provides direct measurements for c_derive. When Kubernetes downgraded from Bazel to Go Build, full builds became **23-39% slower** and incremental builds became **up to 75% slower** Ranjan et al., "The Cost of Downgrading Build Systems," arXiv:2510.20041 [55]. However, Bazel imposed **81-351% higher memory footprint** for full builds and **119-218% higher** for incremental builds. The study estimated that downgrading could increase CI resource costs by a measurable percentage, demonstrating the c_derive vs. c_money trade-off directly.

| Literature Domain | Cost Axes Addressed | Key Correlation/Effect | Source |
|---|---|---|---|
| Hick's Law / IR | c_find | RT = a + b*log2(n); 58% load increase 5->15 items | Atticus Li, 2026 [21] |
| DORA Metrics | c_modify, c_reverse, c_loss | 2 clusters: throughput vs stability | Octopus Deploy [3] |
| SPACE Framework | c_find, c_modify, c_onboard | 5 interconnected dims; productivity-satisfaction correlated | Forsgren et al., ACM Queue [31] |
| Storage Tiering | c_storage, c_find, c_loss | 100x cost differential; inverse storage-retrieval correlation | Data Lingua [19] |
| Architecture Erosion | c_drift, c_onboard, c_modify | Erosion causally drives 3+ other costs; up to 40% budget overrun | Li et al., arXiv [52] |
| Digital Preservation | c_loss | 38% page loss over decade; 54% Wikipedia pages have dead links | Pew Research, 2024 [65] |
| DevEx Research | c_find, c_modify | Flow state -> 50% more productive; high understanding -> 42% more | Forsgren, Microsoft [72] |
| Build Systems | c_derive, c_money | Bazel 23-75% faster than Go Build; 81-351% higher memory | Ranjan et al., arXiv [55] |
| Tech Debt Tools | c_drift, c_modify | Low cross-tool agreement; multiple underlying constructs | Lenarduzzi et al., 2020 [43] |

The table above summarizes cross-domain evidence. No single literature domain covers all nine axes, but the union of these domains touches every axis at least once. The strongest quantitative evidence exists for c_find (Hick's Law), c_loss (Pew link rot), c_storage (cloud pricing), and c_derive (build system benchmarks). The weakest quantitative evidence exists for c_drift (mostly qualitative practitioner reports) and c_reverse (conceptual frameworks but no empirical cost curves).

---

## 2. Per-Axis Measurement Procedures, Units, and Confounders

### c_find -- Time to Locate an Artifact

**(a) Measurement procedure**: Well-established. Information retrieval literature uses time-to-first-relevant-result. In software contexts, measure wall-clock time from task assignment to first file-open of the relevant artifact. The SPACE framework captures this under "Efficiency and flow" via system-level time measures Forsgren et al., ACM Queue [31]. **(b) Units**: Seconds or minutes. **(c) Confounders**: Developer familiarity with codebase (learning curve), quality of search tooling (IDE, grep, code search), naming conventions, and documentation quality. Hick's Law predicts logarithmic scaling with repository size, but actual search tools may linearize or flatten this relationship.

### c_modify -- Time to Change an Artifact

**(a) Measurement procedure**: Defensible via DORA's "lead time for changes" metric, measured from code commit to production deployment. At a finer grain, change coupling studies measure the number of files touched per logical change Hassan, "Predicting the Change Impact of Resolving Defects," 2012 [41]. **(b) Units**: Minutes to hours for individual changes; person-days for features. **(c) Confounders**: Developer skill level, code complexity (cyclomatic complexity), test suite coverage and speed, review process overhead. The DevEx research shows developers with high code understanding feel 42% more productive Microsoft DevEx, 2024 [72], indicating that c_modify confounds with developer knowledge state.

### c_storage -- Bytes on Disk/Cloud

**(a) Measurement procedure**: Directly measurable via file system APIs, cloud billing dashboards, or du/df commands. Well-defined. **(b) Units**: Bytes (typically GB or TB). **(c) Confounders**: Compression ratios, deduplication, versioning overhead (e.g., git objects), derived artifacts stored vs. generated on demand. Storage tiering means the "cost per byte" varies by access pattern Data Lingua [19].

### c_money -- Dollar Cost of Operating the Architecture

**(a) Measurement procedure**: Partially defensible. Cloud billing provides direct infrastructure costs. Developer time costs require salary data and time allocation. **(b) Units**: USD per month or per year. **(c) Confounders**: Shared infrastructure allocation, opportunity costs, hidden costs of architecture debt (up to 40% of transformation budgets per The New Stack [51]). c_money is arguably a composite of all other axes weighted by their unit costs, making it potentially linearly dependent on the other eight.

### c_onboard -- Time for a New Contributor to Become Productive

**(a) Measurement procedure**: Measured as time-to-first-commit or time-to-first-meaningful-PR. The SPACE framework maps this as a proxy for the Communication and collaboration dimension Forsgren et al., ACM Queue [31]. Codebase complexity metrics (cyclomatic complexity, module count) serve as structural proxies. **(b) Units**: Days or weeks. **(c) Confounders**: Heavily confounded by team practices (mentoring, documentation quality, pair programming), prior experience of the contributor, and tooling environment. This is one of the axes most sensitive to non-architectural factors.

### c_drift -- Rate of Architectural Integrity Decay

**(a) Measurement procedure**: The literature offers "architectural smell density" (smells per KLOC) tracked across versions Li et al., arXiv:2103.11392 [52]. Architecture conformance checking tools (Lattix, Sonargraph, Structure101) can measure violations of intended dependency rules. However, this requires an explicit "intended architecture" as baseline. **(b) Units**: Violations per KLOC per release, or percentage deviation from intended architecture. **(c) Confounders**: Whether an intended architecture is documented; team size and turnover rate; development methodology (agile without long-term architecture strategy accelerates drift). **Literature gap**: No standardized measurement procedure exists; most evidence is qualitative from practitioner surveys.

### c_reverse -- Cost of Undoing a Mistaken Operation

**(a) Measurement procedure**: The literature provides conceptual frameworks (Type 1 irreversible vs. Type 2 reversible decisions, attributed to Bezos) and cost-of-change curves that show exponential growth over time ArchMan, "Architectural Decision Impact & Cost of Change" [37]. For operational mistakes (wrong mv/rm), measurement is straightforward in version-controlled systems (git revert time) but poorly defined for non-versioned artifacts. **(b) Units**: Minutes for version-controlled reversals; person-days for architectural decisions. **(c) Confounders**: Heavily dependent on tooling (version control, backup systems, undo capabilities). **Literature gap**: No empirical cost distribution for reversals across project types.

### c_loss -- Probability per Unit Time of Misplacement/Overwrite/Orphan/Dead Link

**(a) Measurement procedure**: Pew Research provides macro-level base rates: approximately **2.5% annual page loss rate** (derived from 25% over 10 years) Pew Research, 2024 [65]. Within software projects, dead link detection is automatable. Orphan file detection requires dependency graph analysis. **(b) Units**: Probability per year, or events per 1000 artifacts per year. **(c) Confounders**: Platform stability (self-hosted vs. cloud), link checking automation, reference management practices. The OAIS reference model provides a conceptual framework but not quantitative rates OAIS, ISO 14721 [11].

### c_derive -- Cost of Regenerating Derived Views

**(a) Measurement procedure**: Directly measurable via build system instrumentation. The Kubernetes study measured full and incremental build times precisely Ranjan et al., arXiv:2510.20041 [55]. CI/CD pipeline logs provide timestamps. **(b) Units**: Seconds or minutes per build; CPU-hours for CI cost. **(c) Confounders**: Build system choice (Bazel vs. Make vs. language-specific tools), caching effectiveness, parallelism settings, hardware allocation. The Kubernetes study found that build tool choice alone accounts for 23-75% variation in build time, suggesting tooling dominates architecture effects.

| Axis | Measurement Quality | Units | Primary Confounders | Literature Depth |
|---|---|---|---|---|
| c_find | Strong (Hick's Law, IR) | Seconds/minutes | Search tooling, familiarity | Deep |
| c_modify | Strong (DORA lead time) | Minutes/hours | Developer skill, test suite | Deep |
| c_storage | Very strong (direct) | Bytes (GB/TB) | Compression, dedup, versioning | Deep |
| c_money | Moderate (billing data) | USD/month | Allocation, hidden costs | Moderate |
| c_onboard | Moderate (time-to-commit) | Days/weeks | Team practices, experience | Moderate |
| c_drift | Weak (smell density) | Violations/KLOC/release | Intended architecture doc | Weak |
| c_reverse | Weak (conceptual only) | Minutes to person-days | Version control, backups | Weak |
| c_loss | Moderate (link rot rates) | Events/1000 artifacts/yr | Platform stability, automation | Moderate |
| c_derive | Strong (build benchmarks) | Seconds/minutes per build | Build tool choice, caching | Moderate |

The table highlights a measurement maturity gap: c_find, c_modify, c_storage, and c_derive have strong measurement procedures grounded in established research, while c_drift and c_reverse lack standardized empirical protocols. This measurement gap itself affects practical rank estimation -- poorly measured axes contribute more noise than signal.

---

## 3. Effective Rank Bounds

### 3.1 Theoretical Rank with Perfect Measurement

If all nine axes could be measured with perfect precision, the effective rank depends on the true correlation structure of the underlying architecture space. Multiple lines of evidence constrain this:

**Lower bound (theoretical): 3.** Three latent factors could plausibly generate all nine observed dimensions: (1) a "structural complexity" factor driving c_find, c_modify, c_onboard, and c_drift simultaneously; (2) a "storage economics" factor driving c_storage, c_loss, and the retrieval component of c_find; (3) a "operational cost" factor driving c_money, c_derive, and c_reverse. The COCOMO II precedent of reducing 17 drivers to 4 categories, and then further to 7 composite factors in the Early Design model, supports aggressive dimensionality reduction DataCamp COCOMO Tutorial [30].

**Upper bound (theoretical): 6.** Even with strong correlations, several axes have independent variation: c_money includes pricing factors orthogonal to structural complexity; c_loss has stochastic components (hardware failure, platform shutdown) independent of architecture; c_derive depends on build-system design choices distinct from code complexity. The SPACE framework's finding that its 5 dimensions are interconnected but in tension -- "optimizing for individual efficiency may decrease collaboration" -- suggests that even correlated dimensions retain residual orthogonal components Forsgren et al., ACM Queue [31].

### 3.2 Practical Rank from Observed Projects

In practice, measurement noise and confounders inflate apparent dimensionality. The technical debt tool comparison study found that different tools measuring "the same construct" produce substantially different rankings Lenarduzzi et al., 2020 [43], suggesting that measurement error adds at least 1-2 apparent dimensions.

**Practical estimate: 4-5 effective dimensions.** This is supported by convergent evidence:
- DORA's 2-cluster structure suggests at minimum 2 independent factors
- Adding the storage-economics factor (c_storage/c_loss/c_find) gives a third
- c_money as a partially independent composite adds a fourth
- c_drift's unique temporal nature (rate rather than point-in-time cost) likely adds a fifth
- c_derive may or may not collapse into the structural complexity factor depending on build system coupling

The prior hypothesis of 4-5 effective dimensions is thus well-supported. The c_find/c_modify clustering hypothesis is strongly supported by the shared cognitive-load mechanism documented in DevEx research. The c_storage/c_loss clustering hypothesis is supported by storage tiering economics, though the correlation is mediated by redundancy policy rather than being a direct structural dependency.

---

## 4. Correlated and Near-Orthogonal Axis Pairs

### 4.1 Strongly Correlated Pairs (Expected |r| > 0.5)

**c_find <-> c_modify**: Both driven by structural complexity and cognitive load. The DevEx research showing that code understanding affects both navigation and modification productivity by 42-50% supports strong positive correlation Microsoft DevEx, 2024 [72]. Mechanism: complex dependency graphs simultaneously make artifacts harder to locate and harder to change safely.

**c_drift <-> c_onboard**: Architecture erosion directly impedes onboarding by making the system harder to comprehend. Li et al. found that eroded architecture makes it "difficult to grasp the original design" Li et al., arXiv:2103.11392 [52]. Mechanism: as intended architecture diverges from implementation, documentation becomes misleading and mental models harder to form.

**c_drift <-> c_modify**: Erosion increases modification cost through accumulated structural violations. This is the core technical/architecture debt mechanism: shortcuts create future modification overhead. Mechanism: cyclic dependencies and violated module boundaries mean changes propagate unpredictably.

**c_storage <-> c_loss**: Storage tiering economics create a direct trade-off where cheaper storage provides less redundancy and durability Data Lingua [19]. However, the correlation is negative in terms of cost: lower c_storage (cheaper) correlates with higher c_loss (more risk). Mechanism: economic optimization by storage providers.

**c_find <-> c_onboard**: Both driven by system comprehensibility. New contributors face the highest c_find costs, and systems with high c_find for experts have proportionally even higher c_find for newcomers due to the absence of tacit knowledge.

### 4.2 Near-Orthogonal Pairs (Expected |r| < 0.2)

**c_storage <-> c_modify**: The number of bytes stored has minimal direct relationship with how long it takes to change a specific artifact. A repository could be large (high c_storage) due to binary assets while having simple, easily-modified source code. Mechanism: storage volume and code complexity are driven by different architectural choices.

**c_money <-> c_drift**: Dollar cost of operations (hosting, CI, licenses) can remain stable or even decrease while architectural integrity silently decays. Cloud bills do not reflect design debt until a breaking point. Mechanism: operational costs are driven by usage patterns and pricing, while drift is driven by development practices.

**c_reverse <-> c_derive**: The cost of undoing a mistake (git revert, database rollback) has little structural relationship with the cost of regenerating derived views (build time, report generation). Mechanism: reversibility depends on version control and backup infrastructure, while derivation depends on build system design and compilation complexity.

**c_loss <-> c_derive**: The probability of information loss (dead links, orphaned files) is largely independent of how expensive it is to regenerate derived artifacts. Mechanism: loss is driven by reference management and platform stability, while derivation cost is driven by build pipeline design.

| Pair | Expected Correlation | Mechanism | Evidence Strength |
|---|---|---|---|
| c_find <-> c_modify | Strong positive (>0.5) | Shared cognitive load, structural complexity | Strong (DevEx, SPACE) |
| c_drift <-> c_onboard | Strong positive (>0.5) | Erosion impedes comprehension | Moderate (Li et al.) |
| c_drift <-> c_modify | Strong positive (>0.5) | Accumulated structural violations | Moderate (architecture debt lit) |
| c_storage <-> c_loss | Moderate negative (-0.3 to -0.5) | Storage tiering economics | Strong (cloud pricing data) |
| c_find <-> c_onboard | Moderate positive (0.3-0.5) | System comprehensibility | Moderate (SPACE framework) |
| c_storage <-> c_modify | Near-orthogonal (<0.2) | Different architectural drivers | Weak (inferred) |
| c_money <-> c_drift | Near-orthogonal (<0.2) | Different temporal dynamics | Weak (inferred) |
| c_reverse <-> c_derive | Near-orthogonal (<0.2) | Independent infrastructure | Weak (inferred) |
| c_loss <-> c_derive | Near-orthogonal (<0.2) | Independent mechanisms | Weak (inferred) |

This table reveals an important asymmetry: the strongly correlated pairs have moderate-to-strong empirical evidence, while the near-orthogonal claims are largely inferred from mechanistic reasoning rather than measured. This is a key gap for the recommended empirical study.

---

## 5. Minimum Data Collection Requirements

### 5.1 Sample Size for PCA with 9 Variables

The traditional rules of thumb for factor analysis sample size recommend 5:1 to 10:1 subjects-to-variables ratios, yielding **45 to 90 observations** for 9 variables The Analysis Factor, "How Big of a Sample Size do you need for Factor Analysis?" [62]. However, recent simulation studies show that the actual requirement depends heavily on communality levels (the proportion of variance in each variable explained by the extracted factors):

- **High communalities (>0.6)**: As few as 50 observations may suffice for stable factor extraction, even with few variables.
- **Low communalities (<0.4)**: 200-500+ observations may be needed, as weak factor loadings require more data to distinguish from noise.
- **Mixed communalities**: The weakest variables dominate sample size requirements.

Given that several of our axes (c_drift, c_reverse) have weak measurement procedures that will produce low communalities, a practical minimum is **60-100 project-architecture observations**.

### 5.2 What Constitutes an "Observation"

Each observation is one project-architecture configuration measured across all 9 axes. Sources of variation:

- **Different repositories**: 10-15 repositories of varied size, domain, and architecture style
- **Different time points**: Each repository measured at 3-5 historical snapshots (leveraging git history)
- **Different task types**: For c_find and c_modify, multiple task types per repository

This yields approximately 10 repos x 4 snapshots x 2 task types = **80 observations**, which falls within the recommended range.

### 5.3 Recommended Measurement Protocol

For each observation, collect:

1. **c_find**: Timed artifact-location tasks using think-aloud protocol or IDE telemetry (3-5 tasks per snapshot)
2. **c_modify**: DORA-style lead time for standardized change types; or historical PR merge times
3. **c_storage**: du -sh on repository; cloud billing for deployed artifacts
4. **c_money**: Monthly cloud/hosting bill + allocated developer cost
5. **c_onboard**: Time-to-first-meaningful-commit for new contributors (from git log)
6. **c_drift**: Architectural smell density via SonarQube or Sonargraph
7. **c_reverse**: Timed reversion exercises; or historical revert PR data from git log
8. **c_loss**: Automated dead-link scan + orphan-file detection at each snapshot
9. **c_derive**: CI build time from pipeline logs (full + incremental)

### 5.4 Minimum Viable Study

The smallest study that could credibly estimate effective rank:

- **10 repositories** spanning: 2 monorepos, 2 multi-repo microservices, 2 documentation-heavy knowledge bases, 2 data pipelines, 2 mixed (code + docs)
- **5 snapshots each** at roughly annual intervals (using git history)
- **3 standardized tasks** per snapshot for c_find and c_modify
- **Total**: 50 primary observations, expanded to approximately 75 with task-level variation
- **Duration**: Approximately 2-3 person-months for data collection; 1 week for PCA analysis
- **Validation**: Bootstrap confidence intervals on eigenvalues to assess rank stability

---

## 6. Intrinsic vs. Environmental Axes

A critical question is whether each axis measures an intrinsic property of the architecture or a property of the team/tooling environment that happens to interact with architecture. This distinction matters because environmental axes should be modeled as parameters (covariates) rather than as dimensions of the architecture's cost signature.

### 6.1 Classification Framework

Following the COCOMO II precedent of separating "product" factors from "personnel" and "project" factors DataCamp COCOMO Tutorial [30], we can classify each axis:

| Axis | Intrinsic to Architecture? | Environmental Component | Recommendation |
|---|---|---|---|
| c_find | Mostly intrinsic | Search tooling quality | Keep in C; control for tooling |
| c_modify | Mostly intrinsic | Developer skill, IDE | Keep in C; control for skill |
| c_storage | Fully intrinsic | None significant | Keep in C |
| c_money | Mixed | Pricing, team size | Keep in C with normalization |
| c_onboard | Mixed-to-environmental | Mentoring, docs culture | Consider moving to parameter |
| c_drift | Mostly intrinsic | Team discipline | Keep in C; control for team |
| c_reverse | Mostly environmental | VCS, backup tools | Move to parameter |
| c_loss | Mixed | Platform stability | Keep in C with platform control |
| c_derive | Mixed | Build tool choice | Keep in C; control for tooling |

### 6.2 Axes to Consider Moving Out of C

**c_reverse** is the strongest candidate for removal. The cost of undoing a mistake is almost entirely determined by the tooling environment: a project using git with frequent commits has near-zero c_reverse for file operations, regardless of architectural complexity. The Kubernetes build study showed that build tool choice alone accounts for massive variation Ranjan et al., arXiv:2510.20041 [55], and the same principle applies more strongly to reversibility -- it is a property of the undo infrastructure, not the architecture being undone.

**c_onboard** is a secondary candidate. While architectural complexity genuinely affects onboarding time, the SPACE framework explicitly notes that onboarding is mediated by Communication and collaboration practices Forsgren et al., ACM Queue [31]. Teams with strong mentoring, documentation, and pair-programming cultures can dramatically reduce c_onboard even for complex architectures. The architecture erosion literature confirms that erosion increases onboarding difficulty Li et al., arXiv:2103.11392 [52], but this effect is already captured through c_drift -> c_onboard correlation.

**c_money** occupies a special position: it is arguably a linear combination of the other axes weighted by their respective unit costs. If c_money = w1*c_find + w2*c_modify + ... + w8*c_derive (for appropriate weights), it is mechanistically linearly dependent and should be derivable rather than independently measured. However, c_money includes components (licensing fees, fixed infrastructure costs) that are genuinely orthogonal to the other axes, so partial retention is defensible.

### 6.3 Implications for Effective Rank

If c_reverse is removed and c_onboard is reclassified as a parameter, the cost vector reduces to 7 intrinsic dimensions. With the same correlation structure, the effective rank drops to approximately **3-4**, and the measurement burden for empirical validation decreases proportionally.

---

## Synthesis: Cross-Cutting Insights and Tensions

### Three Convergent Lines of Evidence for Low Effective Rank

The most striking finding across all literature domains is the consistent evidence for dimensionality reduction. COCOMO II reduces 17 to 4 categories. DORA reduces continuous performance space to 2 clusters. The SPACE framework identifies 5 dimensions but acknowledges they are "deeply interconnected." DevEx research identifies 3 factors (flow, cognitive load, feedback loops). In every case, the empirically observed effective dimensionality is roughly one-third to one-half of the nominal dimensionality. Applied to our 9-axis vector, this consistently predicts **3-5 effective dimensions**.

### The c_drift Hub Phenomenon

Architecture erosion (c_drift) emerges as a uniquely important axis -- not because it is the most measurable (it is among the least), but because it causally influences at least three other axes (c_find, c_modify, c_onboard) and correlates with a fourth (c_loss, through neglect of link maintenance). In factor analysis terms, c_drift likely loads heavily on the primary factor. This "hub" structure is consistent with the architecture debt literature's finding that architectural problems have systemic, cross-cutting consequences, unlike code-level technical debt which tends to be localized The New Stack, 2025 [51].

The tension here is that c_drift is simultaneously the most influential axis and the hardest to measure. Tools like Sonargraph, Lattix, and SonarQube can detect specific architectural smells, but they disagree significantly on what constitutes technical debt Lenarduzzi et al., 2020 [43]. This creates a practical paradox: the axis that would most reduce effective rank if measured well is the one whose measurement noise most inflates apparent dimensionality.

### The Storage-Economics Subspace

The c_storage/c_loss/c_find triad forms a coherent subspace driven by a single underlying parameter: data temperature. Hot data is expensive to store, cheap to retrieve, and well-protected against loss. Cold data is cheap to store, expensive to retrieve, and stored with minimal redundancy. This is not merely correlational but structurally determined by cloud provider economics Data Lingua [19]. The implication is that a single "data temperature" parameter could replace three separate measurements for the storage-related portion of the cost vector, further reducing effective rank.

### Divergence: Theoretical vs. Practical Rank

A critical tension exists between the theoretical and practical rank. Theoretically, with perfect measurement, 3 latent factors might suffice. Practically, measurement noise (especially for c_drift, c_reverse, c_loss) inflates apparent dimensionality. This divergence is exactly what the technical debt tool comparison study illustrates: tools measuring "the same construct" produce different numbers, adding artificial variance Lenarduzzi et al., 2020 [43]. The practical implication is that improving measurement quality for poorly-measured axes (particularly c_drift) would simultaneously reveal the true factor structure and enable more efficient architecture evaluation.

### What the Literature Does Not Yet Support

Honesty requires acknowledging significant gaps:

1. **No study directly measures all 9 axes simultaneously.** Our correlation estimates are synthesized from separate literatures that each cover 2-4 axes.
2. **No correlation coefficients are available for most axis pairs.** The strong/weak correlation assignments in Section 4 are based on mechanistic reasoning, not measured r-values.
3. **The c_reverse axis has essentially no empirical measurement literature.** The Type 1/Type 2 framework is conceptual, not quantitative.
4. **c_derive has been studied only in the context of compiled software**, not knowledge management systems where "derived views" might mean generated documentation, rendered dashboards, or search indexes.
5. **Cross-domain validity is assumed but not tested.** Whether storage tiering correlations observed in cloud infrastructure apply to local file systems or knowledge repositories is unknown.

---

## 7. Recommended Next Experiment

### Study Design: Minimum Viable Rank Estimation

**Objective**: Empirically determine the effective rank of the 9-dimensional cost vector C across a diverse portfolio of software and knowledge projects.

**Design**:
- **Sample**: 12 repositories (3 each from: monorepo codebases, microservice architectures, documentation/knowledge bases, data pipeline projects)
- **Snapshots**: 5 historical snapshots per repository at roughly annual intervals, yielding 60 primary observations
- **Tasks**: For c_find and c_modify, 3 standardized tasks per snapshot (locating a specific function, modifying a configuration parameter, tracing a dependency), expanding effective sample to approximately 80
- **Duration**: 3 person-months for data collection; 2 weeks for analysis
- **Cost**: Approximately $30,000-$50,000 in researcher time

**Measurement protocol per observation**:

| Axis | Instrument | Time per Observation |
|---|---|---|
| c_find | Timed search tasks + IDE telemetry | 30 min |
| c_modify | Historical PR merge time from git log | 15 min (automated) |
| c_storage | du + cloud billing API | 5 min (automated) |
| c_money | Billing records + salary allocation | 30 min |
| c_onboard | Time-to-first-commit from git log | 10 min (automated) |
| c_drift | SonarQube architectural smell scan | 20 min (semi-automated) |
| c_reverse | Timed revert exercise + git revert history | 20 min |
| c_loss | Dead link scanner + orphan file detector | 15 min (automated) |
| c_derive | CI pipeline build time from logs | 5 min (automated) |

**Analysis plan**:
1. Standardize all 9 axes to z-scores
2. Compute 9x9 correlation matrix with bootstrap confidence intervals (1000 resamples)
3. Run PCA; determine effective rank via parallel analysis (compare observed eigenvalues to random-data eigenvalues)
4. Validate with minimum average partial (MAP) criterion and Bayesian information criterion (BIC) for factor models
5. Report scree plot, cumulative variance explained, and factor loading matrix
6. Test the specific hypotheses: (a) c_find/c_modify cluster, (b) c_storage/c_loss cluster, (c) c_drift loads on multiple factors

**Success criteria**: If 4-5 components explain >80% of variance and parallel analysis confirms the same number, the effective rank hypothesis is confirmed. If >6 components are needed, the cost vector is more orthogonal than hypothesized, and all 9 axes should be retained.

**Risk mitigation**: If c_drift measurement proves too noisy (low communality <0.3), run a secondary analysis excluding it, estimating the rank of the remaining 8 axes and treating c_drift as a separately-modeled parameter.

---

## References

1. *The SPACE of Developer Productivity.docx*. http://coursehero.com/file/252817886/The-SPACE-of-Developer-Productivitydocx
2. *How Abridge Scaled Developer Infrastructure from Days to ...*. http://coder.com/blog/how-abridge-scaled-developer-infrastructure-from-days-to-minutes
3. *Understanding the 4 DORA metrics and top findings from 2024/ ...*. https://octopus.com/devops/metrics/dora-metrics/
4. *Cloud DevOps: What the Numbers Can't Hide*. http://ensolvers.com/post/cloud-devops-what-the-numbers-cant-hide
5. *Onboarding Metrics: Measuring Codebase Complexity | PViz Blog*. https://pvizgenerator.com/blog/quantifying-codebase-onboarding
6. *COCOMO and COCOMO II Model- A Case Study - IRJET*. https://www.irjet.net/archives/V7/i5/IRJET-V7I5507.pdf
7. *Analysis Of Software Maintenance Cost Affecting Factors And ...*. https://www.researchgate.net/publication/343670195_Analysis_Of_Software_Maintenance_Cost_Affecting_Factors_And_Estimation_Models
8. *Road and Street Maintenance | Autori*. http://autori.io/solutions/road-and-street-maintenance
9. *Expert Estimation is a first principles cost estimating software ...*. http://facebook.com/pronamics/videos/welcome-to-pronamics-expert-estimation/343104993706215
10. *An Analytical Comparison of Software Project Estimation ...*. https://www.ijcaonline.org/archives/volume187/number1/an-analytical-comparison-of-software-project-estimation-techniques/
11. *Home | OAIS Reference Model (ISO 14721)*. http://www.oais.info/
12. *Risks - Digital Preservation Coalition*. https://www.dpconline.org/digipres/implement-digipres/dpeg-home/dpeg-risks
13. *Designing Storage Architectures for ...*. http://digitalpreservation.gov/meetings/documents/othermeetings/dsa_agenda20090822.pdf
14. *Using PREMIS with METS*. http://loc.gov/standards/premis/premis-mets.html
15. *PREMIS: Preservation Metadata Maintenance Activity (Library ...*. https://www.loc.gov/standards/premis/
16. *Cloud Storage Pricing Comparison: AWS S3, GCP, Azure ...*. http://backblaze.com/cloud-storage/pricing
17. *The Cost Of Risk Management In Data Archiving*. https://asset.fujifilm.com/www/cl/files/2025-09/ab18cbc2b5cd35e12d57a7626ff02062/The_Cost_of_Risk_Management_In_Date_Archiving.pdf
18. *Data Storage Tiers Overview - Logz.io Docs*. http://docs.logz.io/docs/user-guide/admin/data-tiers/data-tiers-intro
19. *Maximize Efficiency with Hot, Warm, Cold Data Storage Strategies*. https://data-lingua.com/hot-warm-cold-data-strategies/
20. *About | Folio Photonics*. http://foliophotonics.com/about
21. *Hick's Law and Navigation Design: The Hidden Cost of Every ...*. https://atticusli.com/blog/posts/hicks-law-navigation-design/
22. *Information Scent Law - Navigation UX Guide - UX/UI Principles*. http://uxuiprinciples.com/en/principles/information-scent
23. *README.md · colbert-ir/colbertv2.0 at main - Hugging Face*. http://huggingface.co/colbert-ir/colbertv2.0/blob/main/README.md
24. *Pricing - Azure AI Search | Microsoft Azure*. https://azure.microsoft.com/en-us/pricing/details/search/
25. *Introduction to Information Retrieval - Stanford University*. https://nlp.stanford.edu/IR-book/pdf/irbookonlinereading.pdf
26. *COCOMO - An Empirical Estimation Model*. https://athena.ecs.csus.edu/~buckley/CSc231_files/COCOMO.pdf
27. [[PDF] RECOMMENDATIONS FOR IMPROVING SOFTWARE COST ...](http://calhoun.nps.edu/bitstream/handle/10945/71130/22Sep_Daley%20et%20al.pdf?sequence=1)
28. *COCOMO II Model Definition Manual*. https://athena.ecs.csus.edu/~buckley/CSc231_files/Cocomo_II_Manual.pdf
29. *COCOMO Models - BOEHM CSSE*. https://boehmcsse.org/tools/cocomo-models/
30. *COCOMO Model: Formula, Types, and Cost Estimation*. https://www.datacamp.com/tutorial/cocomo-model
31. *The SPACE of Developer Productivity - ACM Queue*. https://queue.acm.org/detail.cfm?id=3454124
32. *The SPACE of Developer Productivity: There's more to it than ...*. https://www.microsoft.com/en-us/research/publication/the-space-of-developer-productivity-theres-more-to-it-than-you-think/
33. *How to Measure & Maximize Developer Productivity?*. http://turing.com/resources/developer-productivity
34. *The SPACE metrics: A holistic measure of DevOps productivity*. https://octopus.com/devops/metrics/space-framework/
35. *wbern/claude-instructions*. http://github.com/wbern/claude-instructions
36. *Mastering Reversibility in Software Development - LinkedIn*. https://www.linkedin.com/pulse/mastering-reversibility-software-development-jes%C3%BAs-v%C3%A1zquez-navarro-nqzjf
37. *Architectural Decision Impact & Cost of Change | ArchMan*. https://archman.dev/docs/foundational-concepts/what-is-software-architecture/architectural-decision-impact-and-cost-of-change
38. *Decision-Driven Software Engineering (DDSE) Foundation*. http://github.com/ddse-foundation/ddse-foundation
39. *Design Reversible Strategy: Build Plans You Can Undo Without ...*. https://www.cleverence.com/articles/business-blogs/how-to-design-strategy-that-can-be-reversed-without-damage-4832/
40. *Measuring and Identifying Code-level Technical Debt - Sonar*. http://sonarsource.com/resources/library/measuring-and-identifying-code-level-technical-debt-a-practical-guide
41. *Predicting the Change Impact of Resolving Defects by ...*. https://safwathassan.com/publications/Issure_Reports_Analysis.pdf
42. *Cyclomatic complexity - Wikipedia*. https://en.wikipedia.org/wiki/Cyclomatic_complexity
43. *Evaluating the agreement among technical debt measurement ...*. https://link.springer.com/article/10.1007/s10664-020-09869-w
44. *An Empirical Study of the Relation Between Strong Change ...*. https://link.springer.com/content/pdf/10.1007/978-3-319-17837-0_1.pdf
45. *On the Empirical Evidence of Microservice Logical Coupling*. https://arxiv.org/pdf/2306.02036
46. *HYMAX Company Overview*. http://hymaxusa.com/company
47. *A Large-Scale Empirical Study of AI-Generated Code in Real ...*. https://arxiv.org/pdf/2603.27130
48. *Causal Language To use or not to use…. - Stanford Medicine*. http://content.medweb.stanford.edu/content/dam/sm/s-spire/documents/Causal-language-for-EBM.pdf
49. *Microservice Logical Coupling: A Preliminary Validation*. https://www.researchgate.net/profile/Valentina-Lenarduzzi/publication/367390985_Microservice_Logical_Coupling_A_Preliminary_Validation/links/63d2263dd9fb5967c206623d/Microservice-Logical-Coupling-A-Preliminary-Validation.pdf
50. *vFunction tool assesses technical debt for app modernization*. http://cio.com/article/350220/vfunction-tool-assesses-technical-debt-for-app-modernization.html
51. *Technical Debt vs. Architecture Debt: Don’t Confuse Them*. https://thenewstack.io/technical-debt-vs-architecture-debt-dont-confuse-them/
52. *Understanding Architecture Erosion: The Practitioners’ Perceptive*. https://arxiv.org/pdf/2103.11392
53. *CAST Software*. http://castsoftware.com/
54. *Accelerate Modernization with Architectural Observability*. http://vfunction.com/blog/architectural-observability-accelerates-app-modernization
55. *The Cost of Downgrading Build Systems: A Case Study of Kubernetes*. https://arxiv.org/pdf/2510.20041
56. *(PDF) Analyzing Project Complexity, Its Dimensions and Their ...*. https://www.researchgate.net/publication/373072019_Analyzing_Project_Complexity_Its_Dimensions_and_Their_Impact_on_Project_Success
57. *Mytos - LinkedIn*. http://linkedin.com/company/mytosbio
58. *Jet.Build homepage*. http://jet.build/
59. *Deep Dive: How Turbopack 2026’s New Incremental Build System ...*. https://johal.in/deep-dive-turbopack-2026s-new-incremental-build-system/
60. *Lead Scoring Case Study | Kaggle*. http://kaggle.com/competitions/lead-scoring-case-study-acpc1/data
61. *A statistical test and sample size recommendations for ...*. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6200243/
62. *How Big of a Sample Size do you need for Factor Analysis?*. https://www.theanalysisfactor.com/sample-size-needed-for-factor-analysis/
63. *Innovative Leaders in Laboratory Automation | ESI*. http://icpms.com/products
64. *Lead Scoring | Akkio Docs*. http://docs.akkio.com/akkio-docs/demo-models/demo-models/lead-scoring
65. *Link Rot and Digital Decay on Government, News and Other ...*. https://www.pewresearch.org/data-labs/2024/05/17/when-online-content-disappears/
66. *Large Scale Study of Orphan Vulnerabilities in the Software ...*. https://par.nsf.gov/servlets/purl/10552599
67. *Publications - Gitler Lab*. http://gitlerlab.org/publications
68. *Gone but Not Forgotten: Recovering the Dead Web*. https://blog.archive.org/2026/04/23/gone-but-not-forgotten-recovering-the-dead-web/
69. *Large Scale Study of Orphan Vulnerabilities in the Software ...*. https://dl.acm.org/doi/10.1145/3617555.3617872
70. *Empirical pathways to developer experience: A facet-based ...*. https://www.sciencedirect.com/science/article/pii/S0164121225003176
71. *Technical Lead - Developer Experience (DevEx) - Arbor Education*. http://careers.arbor-education.com/_/j/0285EEACE7
72. *Quantifying the impact of developer experience | Microsoft ...*. https://azure.microsoft.com/en-us/blog/quantifying-the-impact-of-developer-experience/
73. *Empirical (Software Development Applications)*. http://pitchbook.com/profiles/company/663759-91
74. *COCOMO II Model Overview and Insights | PDF | Software*. http://scribd.com/presentation/52033045/COCOMO-Presentation
75. *COCOMO II Cost Drivers Overview | PDF - Scribd*. https://www.scribd.com/document/498599861/COCOMO-cost-drivers
76. *COCOMO II - msdbok.github.io*. https://msdbok.github.io/content/scope/estimates/cocomo.html
