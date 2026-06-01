# RQ12 — What is the cost of the layer seam?

## Question

Splitting one repo into two (Layer A + Layer B):
- Lowers `c_drift` (engine and tenant evolve on separate clocks).
- Raises `c_modify` (cross-cutting changes now touch two repos + the seam shim).
- Effect on `c_money`, `c_loss`, `c_storage` unclear.

Net cost?

## Stakes

Decides whether two-layer separation is the **default architecture** for K = outbound-pipeline, or an **optimization** triggered when c_drift exceeds a threshold.

## Sub-questions

- Q12.1: Empirical: measure c_modify pre vs post on a real change (e.g., adding a new sender to round-robin) across Buuuk + neural-gtm.
- Q12.2: Closed-form: is there a c_modify(N_layers) growth function?
- Q12.3: When does the seam break? At what N tenants does Layer A's W converge vs diverge?

## Evidence to date

v0.1 consolidation: 111 → 71 primitives (~36% drop). Drop is from IC3 satisfaction, not c_drift measurement directly. So the seam *helps* on the rank-of-violations axis. The actual c_drift / c_modify trade is still TBD.

## Not yet answered

Skeletal placeholder.
