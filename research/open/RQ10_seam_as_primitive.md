# RQ10 — Is the layer seam a primitive of A*?

## Question

The Layer A ⇄ Layer B seam has two invariants (currently enforced only in the QA agent):
- `tenant_cannot_mutate_engine_state`
- `engine_cannot_read_tenant_secrets`

Is this seam:
(a) a **new primitive operation** to add to the 9-op set?
(b) a **new integrity constraint** (IC4)?
(c) **derivable** from IC3 (folder-as-contract) + the existing 9 ops?

## Stakes

If (a) or (b), A_STAR_v0 needs a v0.2 edit. If (c), the QA agent's seam invariants are a worked example of how IC3 already implies multi-layer safety.

## Sub-questions

- Q10.1: If IC4, what is its declarative form? Per-folder declare your `layer: A | B`?
- Q10.2: If primitive op, what's the name? `DECLARE_LAYER`? `BIND_SEAM`?
- Q10.3: Does S(M, T) (routing reduction) generalize to S(M, T, L) where L = layer?

## Not yet answered

Skeletal placeholder.
