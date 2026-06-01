# Architecture-as-Function — `A*(I,L,K,T) → (A,D)`

> A meta-equation that expresses any AI engineering surface as a function. Implemented in production as the Neural Conductor. Open source.

## The equation

$$
A^*\!:\;(I, L, K, T) \;\to\; (A, D)
$$

Every AI surface is a function over:

- **$I$** Inputs (signals the surface receives)
- **$L$** Levers (controls it can move)
- **$K$** Knowledge (state, history, models, plans, policies, values, meta)
- **$T$** Tasks (decomposed work)

producing:

- **$A$** Actions (effects on the world)
- **$D$** Decisions (which option of which set, given a score)

with the **Decision sub-function reducing canonically to $S(M,T)$** (see [shadow-router](https://github.com/pranavlakherwal/shadow-router)).

## Why it exists

Large AI organisations build the same kind of surface over and over: an inference server, an agentic CLI, a computer-use agent, an evaluation harness, an enterprise integration pod. Each team invents its own routing, its own evaluation, its own reward. Headcount scales with number of surfaces.

$A^*$ is one shared primitive structure underneath all of them. Every surface has the same internal modules ($I$-, $L$-, $K$-, $T$-, $A$-, $D$-), differing only in concrete content.

## Derivation (first principles)

Asking *what is the smallest structure an autonomous system needs to be expressible as code* yields four irreducible pieces (what it knows, what it can change, what it observes, what it must do) and two outputs (what it does, how it decides). The rest of the framework is the typing.

- **7 $C_{\text{core}}$ axes:** identity, inputs, levers, knowledge, tasks, actions, decisions.
- **3 information conditions:** observability, controllability, identifiability.
- **7-class knowledge typing:** state, history, model, plan, policy, value, meta.
- **9 primitive operations:** read, write, infer, plan, act, learn, verify, route, compose.
- **Z3 Optimize** as the closed-form constraint solver.
- **$D \to S(M,T)$** as the canonical decision reduction.

Full derivation in `docs/derivation.pdf`.

## Worked example: Grok-style coding-agent CLI

| Slot | Concrete content |
|---|---|
| $I$ | user prompt + `AGENTS.md` + repo handle + history |
| $L$ | $\{$sub-agent count $\in [1..8]$, worktree assignment, model per sub-agent, reasoning effort, plan-mode$\}$ |
| $K$ | repo embeddings, recent edits, tool catalog, MCP server outputs, prior plans |
| $T$ | decomposed sub-tasks (read, write, test, refactor) |
| $A$ | $\{$spawn sub-agent, edit file, run test, open PR$\}$ |
| $D$ | for each sub-task, pick $(\text{model}, \text{effort}, \text{agent}) = S(M,T)$ |

The same expansion holds for an **inference server** ($L$ = quant level, KV cache placement, batch size, spec-decode draft), a **computer-use agent** ($L$ = navigator-vs-vision, action granularity), and an **enterprise integration** ($L$ = tier, SLA, fine-tune-vs-RAG).

One skeleton, many product surfaces.

## Production

Implemented as the **Neural Conductor**, 6 layers:

- **L0 Substrate** — event bus, daemon, ReviewQueue (the `K` module + `read`/`write`).
- **L1 Sense** — registry scanner + scorecard (the `K` module's discovery layer).
- **L2 Maintain** — sentinel + bridge (the `verify` + `route` operations).
- **L3 Autonomy** — PreToolUse policy hook with 3-tier auto-approve (the `L` → `A` projection with safety gating).
- **L4 Conduct** — opportunity scorer running $S(A,O)$ (the $D$ surface).
- **L5 Scholar** — the academic-research loop (parked).

Runs as a long-lived daemon over a 50+ agent stack supporting five live products. P0 through P4 shipped between 2026-05-18 and 2026-05-20. Tests: 49/49 green at last sign-off.

## What this repo contains

```
architecture-as-function/
├── README.md                              # you are here
├── LICENSE                                # Apache 2.0
├── docs/
│   ├── astar_abstract.pdf                 # one-page abstract (arXiv-shaped)
│   ├── derivation.pdf                     # full derivation (7 axes, 3 ICs, 7-class K, 9 ops, Z3)
│   ├── neural_conductor.md                # L0-L5 architecture and current implementation
│   └── worked_examples/                   # A* applied to 6+ surfaces, line by line
├── astar/                                 # reference Python implementation
│   ├── __init__.py
│   ├── types.py                           # I, L, K, T, A, D dataclasses
│   ├── smt.py                             # the decision sub-function (links to shadow-router)
│   ├── primitives.py                      # the 9 primitive operations
│   ├── optimize.py                        # Z3 Optimize wrapper
│   └── conductor/                         # the L0-L5 layer implementations
└── examples/
    ├── grok_build_cli.py                  # A* applied to a coding agent
    ├── inference_server.py                # A* applied to a serving engine
    └── computer_use_agent.py              # A* applied to a Macrohard-style loop
```

## Status

| Component | Status |
|---|---|
| 7-axis derivation | frozen 2026-05-21 |
| Neural Conductor L0-L4 | shipped, 49/49 tests green |
| One-page arXiv abstract | drafted |
| Worked examples (coding CLI, inference, computer-use) | drafted |
| L5 Scholar (academic loop) | parked |

## Cite

```bibtex
@misc{lakherwal2026astar,
  author = {Pranav Lakherwal},
  title  = {A*(I,L,K,T)→(A,D): Architecture-as-Function for AI Systems},
  year   = {2026},
  url    = {https://github.com/pranavlakherwal/architecture-as-function}
}
```

## License

Apache 2.0.
