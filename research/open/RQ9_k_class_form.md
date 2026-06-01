# RQ9 — What is the form of K?

## Question

In A*(I, L, K, T) → (A, D), what is the right *form* for K?

Three candidates:
1. **Fixed taxonomy** (v0 status quo). 7 named classes, each a tuple (H_K, W_K, T_K, F_K, E_K).
2. **Inheritance lattice**. Classes derive from each other. `engine-of(outbound-pipeline)` lifts tenant-specific constraints into tenant-agnostic ones.
3. **Free constraint-bag**. K dissolves. Each folder declares its own (H, W, T, F) in its manifest.

## Trigger

`/Core/Neural/neural-gtm/` (Layer A engine) doesn't fit any of the 7 v0 classes. We forced `outbound-pipeline` for the solver run, which is wrong: neural-gtm has no leads, no cohorts, no SMTP.

## Stakes

- Fixed: simple, learnable, but doesn't generalize. Every new pattern needs a new class.
- Lattice: keeps the 7 as bootstrap, adds derivation rules. Best-of-both if derivation is mechanical.
- Free: maximally expressive. Loses the K-as-prior advantage (e.g. weight defaults).

## Open sub-questions

- Q9.1: If lattice, what are the derivation operators? `lift_tenant`, `restrict_scope`, `compose(K1, K2)`?
- Q9.2: If free, how do we recover the simplicity prior H_simp? (Currently encoded via K's W defaults.)
- Q9.3: Does the lattice form change the COP encoding in `solver/model.py`?
- Q9.4: Is there empirical evidence from the 8 existing Neural projects that they cluster into the 7, or that some span multiple classes?

## Not yet answered

Skeletal placeholder. Expand when this question is picked up for a deep-research wave.
